import os, warnings, logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore")
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("mediapipe").setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)

from ultralytics import YOLO
import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
import time

# === your infra ===
from src.model.detection import Detector
from src.model.schema import MLFrame, Prediction, CLASSES, UNKNOWN_CLASS
from src.model.text_corrector import word_check

# ---- tiny knobs (keep model in control) ----
CONF_FLOOR = 0.50          # accept only confident preds (try 0.45–0.70 as needed)
IMG_SIZE   = 640           # YOLO input size (kept simple)
SPELL_FPS  = 3             # max spell-checks per second for on-screen preview

# ---- setup camera & model ----
cap = cv2.VideoCapture(0)
WEIGHTS = (Path(__file__).resolve().parents[2] / "data" / "best.pt")
assert WEIGHTS.exists(), f"Missing weights at: {WEIGHTS}"
model = YOLO(str(WEIGHTS))

# Initialize MediaPipe hands (just for your edge/outline view)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.4,
    min_tracking_confidence=0.4
)
mp_drawing = mp.solutions.drawing_utils

# === temporal detector ===
detector = Detector()

def normalize_class(name: str) -> str:
    if not name:
        return UNKNOWN_CLASS
    n = name.strip()
    if n.lower() in {"space", "blank"} and "space" in CLASSES:
        return "space"
    if n.lower() in {"del", "delete", "backspace"} and "del" in CLASSES:
        return "del"
    if len(n) == 1 and n.isalpha():
        u = n.upper()
        return u if u in CLASSES else UNKNOWN_CLASS
    return n if n in CLASSES else UNKNOWN_CLASS

def yolo_predict_best(frame_bgr):
    """Return (cls_name:str, conf:float). Works for classifier or detector weights."""
    r = model.predict(frame_bgr, imgsz=IMG_SIZE, verbose=False, save=False, stream=False)[0]

    # classification path
    if getattr(r, "probs", None) is not None:
        names = r.names if hasattr(r, "names") else getattr(model, "names", {})
        top1 = int(r.probs.top1)
        top1conf = getattr(r.probs, "top1conf", None)
        conf = float(top1conf.item()) if top1conf is not None else float(r.probs.data.max().item())
        name = names.get(top1, str(top1)) if isinstance(names, dict) else str(top1)
        return name, conf

    # detection path
    boxes = getattr(r, "boxes", None)
    if boxes is not None and len(boxes) > 0:
        confs = boxes.conf.detach().cpu().numpy()
        idx = int(np.argmax(confs))
        conf = float(confs[idx])
        clsid = int(boxes.cls[idx].item())
        names = r.names if hasattr(r, "names") else getattr(model, "names", {})
        name = names.get(clsid, str(clsid)) if isinstance(names, dict) else str(clsid)
        return name, conf

    return UNKNOWN_CLASS, 0.0

print(cap.isOpened())

# --- spell preview throttling ---
last_spell_t = 0.0
live_sentence_cache = ""

quit_now = False
try:
    while cap.isOpened() and not quit_now:
        ret, img = cap.read()
        if not ret:
            break

        # mirror for UX
        img = cv2.flip(img, 1)

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process the frame (for your visual mask)
        results = hands.process(rgb_frame)

        # Edge detection on original image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Invert edges: black edges on white background
        edges = cv2.bitwise_not(edges)

        # Convert edges to 3-channel
        mask = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Draw MediaPipe hand connections (visual only)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    mask,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

        # === YOLO on your mask image ===
        raw_label, conf = yolo_predict_best(mask)

        # minimal gating so we don't block the model
        cls = normalize_class(raw_label)
        if conf < CONF_FLOOR:
            cls, conf = UNKNOWN_CLASS, 0.0

        # === feed Detector (same as your old flow) ===
        ts = int(time.time() * 1000)
        detector.update(MLFrame(
            timestamp_ms=ts,
            hand_present=(cls != UNKNOWN_CLASS),
            predictions=[Prediction(cls=cls, prob=conf)]
        ))

        # draw YOLO class/score on the mask (optional)
        if cls != UNKNOWN_CLASS:
            cv2.putText(mask, f"{cls}:{conf:.2f}", (10, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 180, 0), 2)

        # === overlay buffer + live sentence on the camera window ===
        snap = detector.snapshot()
        live_buffer = snap.buffer

        # Debounce spell-check (heavy) to ~SPELL_FPS
        now = time.time()
        if now - last_spell_t >= (1.0 / max(1, SPELL_FPS)):
            try:
                live_sentence_cache = word_check(live_buffer.replace("WW", " ").strip())
            except Exception:
                # fallback: show raw buffer if spell-check has issues
                live_sentence_cache = live_buffer.replace("WW", " ").strip()
            last_spell_t = now

        # put overlays on the LEFT (original) view so it’s visible while edges stay clean
        cv2.putText(img, f"Buffer: {live_buffer}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(img, f"Sentence: {live_sentence_cache}", (10, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,255,200), 2)

        # Combine original and mask side by side
        combined = np.hstack((img, mask))

        # Display combined image
        cv2.imshow('Original | Edges + Hand Outline', combined)
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):
            quit_now = True

except KeyboardInterrupt:
    # Gracefully stop on Ctrl-C; we'll still print the final sentence below.
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
    # Always attempt one final spelling pass on the full buffer
    final_buffer = detector.snapshot().buffer.replace("WW", " ").strip()
    try:
        final_sentence = word_check(final_buffer)
    except Exception:
        final_sentence = final_buffer
    print("\nFINAL SENTENCE:", final_sentence, flush=True)
