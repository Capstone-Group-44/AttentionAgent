# src/config.py
import os

# Project root (folder that contains main.py)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Data paths
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, "focus_data.csv")

# Model output path
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "focus_xgb_pipeline.joblib")

# Train/test split + randomness
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Target column name
TARGET_COLUMN = "focused?"

# Columns expected in the dataset (for reference / validation)
EXPECTED_COLUMNS = [
    "timestamp",
    "screen_width",
    "screen_height",
    "left_gaze_x",
    "left_gaze_y",
    "right_gaze_x",
    "right_gaze_y",
    "face_x",
    "face_y",
    "face_z",
    "focused?",
]