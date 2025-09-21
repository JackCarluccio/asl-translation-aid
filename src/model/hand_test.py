from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import cv2 
import mediapipe as mp
import pandas as pd
import kagglehub
import os
import time
import matplotlib.pyplot as plt

# 1. Load the data
df = pd.read_csv("hand_landmarks.csv")


# 2. Split features and labels
X = df.drop("label", axis=1)
y = df["label"]

# 3. Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Train the classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_scaled, y)



# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils
# Start webcam capture
# Download latest version



cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue
    results = hands.process(image)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            coords = []
            for i, landmark in enumerate(hand_landmarks.landmark):
                coords.append(landmark.x)
                coords.append(landmark.y)
                coords.append(landmark.z)
            if len(coords) == 63:
                coords_scaled = scaler.transform([coords])
                result = clf.predict(coords_scaled)
                print(result)
            else:
                print("Not enough landmarks detected.")
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imshow('ASL Hand Prediction', image)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break
cap.release()
cv2.destroyAllWindows()
            


    

