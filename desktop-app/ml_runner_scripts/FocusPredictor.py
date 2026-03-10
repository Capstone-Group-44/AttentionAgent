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
        self.model = xgb.XGBClassifier()
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
        x = min(xs)
        y = min(ys)
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        return x, y, w, h

    def extract_features(self, landmarks, img_w, img_h):
        xs = [lm.x for lm in landmarks]
        ys = [lm.y for lm in landmarks]
        face_x = min(xs)
        face_y = min(ys)
        face_w = max(xs) - min(xs)
        face_h = max(ys) - min(ys)

        left_eye_idx = [33, 133, 159, 145, 153, 154]
        right_eye_idx = [362, 263, 386, 374, 380, 381]

        left_eye_x, left_eye_y, left_eye_w, left_eye_h = self.get_eye_bbox(
            landmarks, left_eye_idx, img_w, img_h)
        right_eye_x, right_eye_y, right_eye_w, right_eye_h = self.get_eye_bbox(
            landmarks, right_eye_idx, img_w, img_h)

        face_cx = face_x + face_w / 2
        face_cy = face_y + face_h / 2
        left_eye_cx = left_eye_x + left_eye_w / 2
        left_eye_cy = left_eye_y + left_eye_h / 2
        right_eye_cx = right_eye_x + right_eye_w / 2
        right_eye_cy = right_eye_y + right_eye_h / 2

        left_eye_dx = left_eye_cx - face_cx
        left_eye_dy = left_eye_cy - face_cy
        right_eye_dx = right_eye_cx - face_cx
        right_eye_dy = right_eye_cy - face_cy
        sym_dx = left_eye_dx - right_eye_dx
        sym_dy = left_eye_dy - right_eye_dy

        left_eye_corner = landmarks[33]
        right_eye_corner = landmarks[263]
        nose = landmarks[1]
        chin = landmarks[199]
        yaw = right_eye_corner.x - left_eye_corner.x
        pitch = chin.y - nose.y
        roll = (right_eye_corner.y - left_eye_corner.y) / (
            (right_eye_corner.x - left_eye_corner.x) + 1e-6
        )

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
        focused = int(self.model.predict(df)[0])
        prob = float(self.model.predict_proba(df)[0][1])
        return focused, prob
