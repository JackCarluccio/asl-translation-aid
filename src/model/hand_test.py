import os, warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # silence TF/MediaPipe INFO+WARN
warnings.filterwarnings("ignore") 

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import cv2 
import mediapipe as mp
import pandas as pd
import time

# === Imports from your schema/detector ===
from src.data_structures.detection import Detector
from src.data_structures.schema import MLFrame, Prediction, CLASSES, UNKNOWN_CLASS
from src.data_structures.text_corrector import word_check

# 1. Load the data
df = pd.read_csv("src/model/hand_landmarks.csv")

# 2. Split features and labels
X = df.drop("label", axis=1)
y = df["label"]

# 3. Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Train the classifier
clf = RandomForestClassifier(n_estimators=100, random_state=62)
clf.fit(X_scaled, y)

# === Init detector once ===
detector = Detector()

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)
mp_drawing = mp.solutions.drawing_utils

# Start webcam capture
cap = cv2.VideoCapture(0)

quit_now = False
try:
    while cap.isOpened() and not quit_now:
        success, image = cap.read()
        if not success:
            continue

        # Flip & RGB for MediaPipe
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = hands.process(image_rgb)
        image_rgb.flags.writeable = True

        hand_present = results.multi_hand_landmarks is not None
        pred_class, pred_prob = UNKNOWN_CLASS, 0.0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                coords = []
                for lm in hand_landmarks.landmark:
                    coords.extend([lm.x, lm.y, lm.z])

                if len(coords) == 63:
                    coords_scaled = scaler.transform([coords])
                    result = clf.predict(coords_scaled)
                    pred_class_raw = str(result[0]) if len(result) else UNKNOWN_CLASS

                    if hasattr(clf, "predict_proba"):
                        proba_row = clf.predict_proba(coords_scaled)[0]
                        try:
                            idx = list(clf.classes_).index(pred_class_raw)
                            pred_prob = float(proba_row[idx])
                        except ValueError:
                            pred_prob = float(max(proba_row))
                    else:
                        pred_prob = 1.0

                    pred_class = pred_class_raw if pred_class_raw in CLASSES else UNKNOWN_CLASS

                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Detector update
        ts = int(time.time() * 1000)
        frame_for_detector = MLFrame(
            timestamp_ms=ts,
            hand_present=bool(hand_present),
            predictions=[Prediction(cls=pred_class, prob=pred_prob)]
        )
        detector.update(frame_for_detector)

        # Overlay buffer/status
        snap = detector.snapshot()
        cv2.putText(image, f"Buffer: {snap.buffer}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(image, f"Status: {snap.status.value}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)

        cv2.imshow('ASL Hand Prediction', image)

        # ONE waitKey per frame
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):  # ESC or q
            quit_now = True

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
    final_sentence = detector.snapshot().buffer
    final_sentence = final_sentence.replace("WW", " ").strip()
    print("\nFINAL SENTENCE:", word_check(final_sentence), flush=True)