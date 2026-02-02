import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import json
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


MODEL_PATH = "../models/focus_xgb_pipeline.joblib"
model = joblib.load(MODEL_PATH)
print(f"Loaded model from {MODEL_PATH}")


TEST_DATA_PATH = "../data/raw/raw_coordinates_test.csv"
df_test = pd.read_csv(TEST_DATA_PATH).dropna()

X_test = df_test[['screen_width', 'screen_height', 'left_gaze_x', 'left_gaze_y',
                  'right_gaze_x', 'right_gaze_y', 'face_x', 'face_y', 'face_z']]
y_test = df_test['focused?']


y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
clf_report = classification_report(y_test, y_pred, output_dict=True)
cm = confusion_matrix(y_test, y_pred).tolist()

print(f"Test Accuracy: {acc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(np.array(cm))

TEST_RESULTS_PATH = "test_results.json"
test_results = {
    "accuracy": acc,
    "classification_report": clf_report,
    "confusion_matrix": cm
}

with open(TEST_RESULTS_PATH, "w") as f:
    json.dump(test_results, f, indent=4)

print(f"Test results saved at {TEST_RESULTS_PATH}")

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=[0, 1], yticklabels=[0, 1])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()
