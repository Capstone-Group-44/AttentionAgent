import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import os

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(
    BASE_DIR, "..",
    "ml_dev_scripts",
    "docs",
    "loso_results_11_new_data",
    "xgb_model_subject_2_tuned.json"))
DATA_PATH = "C:\\Uni Tests, Assignments, Labs\\Capstone Project\\Manual Collection Dataset\\master_dataset.csv"
TEST_SUBJECT = 1
FEATURE_COLS = [
    'face_x', 'face_y', 'face_w', 'face_h',
    'left_eye_x', 'left_eye_y', 'left_eye_w', 'left_eye_h',
    'right_eye_x', 'right_eye_y', 'right_eye_w', 'right_eye_h',
    'left_eye_dx', 'left_eye_dy',
    'right_eye_dx', 'right_eye_dy', 'sym_dx', 'sym_dy', 'yaw', 'pitch', 'roll'
]
TARGET_COL = 'label'

# === LOAD DATA ===
df = pd.read_csv(DATA_PATH)
test_df = df[df['subject_id'] == TEST_SUBJECT]
X_test = test_df[FEATURE_COLS]
y_test = test_df[TARGET_COL]

dtest = xgb.DMatrix(X_test, label=y_test)

# === LOAD MODEL ===
bst = xgb.Booster()
bst.load_model(MODEL_PATH)

# === PREDICT PROBABILITIES ===
y_pred_prob = bst.predict(dtest)

# === COMPUTE ROC ===
# adjust pos_label if needed
fpr, tpr, _ = roc_curve(y_test, y_pred_prob, pos_label=0)
roc_auc = auc(fpr, tpr)

# === PLOT ===
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2,
         label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title(f'ROC Curve - Subject {TEST_SUBJECT}')
plt.legend(loc='lower right')

# Create results folder if it doesn't exist
os.makedirs("results", exist_ok=True)
plt.savefig(f"results/roc_curve_subject_{TEST_SUBJECT}.png")
plt.close()

print(
    f"ROC curve saved to results/roc_curve_subject_{TEST_SUBJECT}.png with AUC = {roc_auc:.2f}")
