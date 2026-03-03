"""
File Name: FocusPredictor.py
Description: This script is responsible for importing the XGBoost model and for making real-time predictions.
Uses the same feature extraction as the data collection script to ensure consistency. 
"""
import os
import cv2
import mediapipe as mp
import pandas as pd
import xgboost as xgb

FEATURE_COLS = [
    'face_x', 'face_y', 'face_w', 'face_h',
    'left_eye_x', 'left_eye_y', 'left_eye_w', 'left_eye_h',
    'right_eye_x', 'right_eye_y', 'right_eye_w', 'right_eye_h',
    'left_eye_dx', 'left_eye_dy',
    'right_eye_dx', 'right_eye_dy',
    'sym_dx', 'sym_dy', 'yaw', 'pitch', 'roll'
]


class FocusPredictor:
    def __init__(self, model_path):
        self.model = xgb.Booster()
        self.model.load_model(model_path)

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_eye_bbox(self, landmarks, indices, img_w, img_h):
        xs = [landmarks[i].x for i in indices]
        ys = [landmarks[i].y for i in indices]
        x = min(xs) * img_w
        y = min(ys) * img_h
        w = (max(xs) - min(xs)) * img_w
        h = (max(ys) - min(ys)) * img_h
        return x, y, w, h

    def extract_features(self, landmarks, img_w, img_h):
        xs = [lm.x for lm in landmarks]
        ys = [lm.y for lm in landmarks]
        face_x = min(xs) * img_w
        face_y = min(ys) * img_h
        face_w = (max(xs) - min(xs)) * img_w
        face_h = (max(ys) - min(ys)) * img_h

        left_eye_idx = [33, 133, 160, 159, 158, 144]
        right_eye_idx = [362, 263, 387, 386, 385, 373]

        left_eye_x, left_eye_y, left_eye_w, left_eye_h = self.get_eye_bbox(
            landmarks, left_eye_idx, img_w, img_h)
        right_eye_x, right_eye_y, right_eye_w, right_eye_h = self.get_eye_bbox(
            landmarks, right_eye_idx, img_w, img_h)

        left_eye_dx = left_eye_x - face_x
        left_eye_dy = left_eye_y - face_y
        right_eye_dx = right_eye_x - face_x
        right_eye_dy = right_eye_y - face_y
        sym_dx = abs(left_eye_dx - right_eye_dx)
        sym_dy = abs(left_eye_dy - right_eye_dy)
        yaw = landmarks[1].x - landmarks[234].x
        pitch = landmarks[1].y - landmarks[152].y
        roll = landmarks[33].y - landmarks[263].y

        return [
            face_x, face_y, face_w, face_h,
            left_eye_x, left_eye_y, left_eye_w, left_eye_h,
            right_eye_x, right_eye_y, right_eye_w, right_eye_h,
            left_eye_dx, left_eye_dy,
            right_eye_dx, right_eye_dy,
            sym_dx, sym_dy,
            yaw, pitch, roll
        ]

    def predict(self, features):
        df = pd.DataFrame([features], columns=FEATURE_COLS)
        dmatrix = xgb.DMatrix(df)
        prob = self.model.predict(dmatrix)[0]
        focused = int(prob > 0.5)
        return focused, prob
