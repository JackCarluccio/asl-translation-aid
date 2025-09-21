from ultralytics import YOLO
import cv2
import mediapipe as mp
import numpy as np


cap = cv2.VideoCapture(0)
model = YOLO("/home/anthony/steelhacks/asl-translation-aid/data/best.pt") 


# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.4,
    min_tracking_confidence=0.4
)
mp_drawing = mp.solutions.drawing_utils
print(cap.isOpened())
while cap.isOpened():
    ret, img = cap.read()
    if not ret:
        break
    
    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Process the frame
    results = hands.process(rgb_frame)
    # Edge detection on original image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # Invert edges: black edges on white background
    edges = cv2.bitwise_not(edges)
    
    # Convert edges to 3-channel
    mask = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Draw MediaPipe hand connections in red on top of edges
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw connections (outline) in red on top
            mp_drawing.draw_landmarks(
                mask,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=None,  # Don't draw landmark points
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)  # Red outline
            )
       # Run YOLO prediction on the mask

       #HERE
    res = model.predict(mask)
    
    # Draw YOLO results on the mask
    if res[0].boxes is not None:
        for box in res[0].boxes:
            # Get box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            conf = box.conf[0].cpu().numpy()
            cls = int(box.cls[0].cpu().numpy())
            
            # Draw bounding box on mask
            cv2.rectangle(mask, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label with confidence on mask
            label = f"{model.names[cls]}: {conf:.2f}"
            cv2.putText(mask, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Combine original and mask side by side
    combined = np.hstack((img, mask))
    print(res[0])

    
    # Display combined image
    cv2.imshow('Original | Edges + Hand Outline', combined)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
