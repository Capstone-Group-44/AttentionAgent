import xgboost as xgb
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(
    BASE_DIR, "..", "models", "xgb_model_subject_3.json"))
OUTPUT_PATH = os.path.join(BASE_DIR, "tree_top_levels.png")

# Feature names
feature_cols = [
    'face_x', 'face_y', 'face_w', 'face_h',
    'left_eye_x', 'left_eye_y', 'left_eye_w', 'left_eye_h',
    'right_eye_x', 'right_eye_y', 'right_eye_w', 'right_eye_h',
    'left_eye_dx', 'left_eye_dy',
    'right_eye_dx', 'right_eye_dy', 'sym_dx', 'sym_dy',
    'yaw', 'pitch', 'roll'
]

# Load model
booster = xgb.Booster()
booster.load_model(MODEL_PATH)
booster.feature_names = feature_cols

# Create high-res figure
plt.figure(figsize=(40, 20), dpi=300)

# Get graphviz source
dot_data = xgb.to_graphviz(
    booster, tree_idx=0, rankdir='LR', yes_color='green', no_color='red')

# Save graphviz as PNG
dot_data.format = 'png'
dot_data.render(filename=OUTPUT_PATH.replace('.png', ''), cleanup=True)

print("High-resolution top-level tree image saved to:", OUTPUT_PATH)
