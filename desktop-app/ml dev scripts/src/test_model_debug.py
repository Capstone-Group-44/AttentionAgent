from pathlib import Path
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = r"c:\University\Fourth_Year\AttentionAgent\XGBoost\models\focus_xgb_pipeline.joblib"
CSV_PATH   = r"c:\University\Fourth_Year\AttentionAgent\XGBoost\data\raw\focus_data.csv"

print("Loading model...")
model = joblib.load(MODEL_PATH)
print("classes:", model.classes_)  # should be [0 1]

print("\nLoading CSV...")
df = pd.read_csv(CSV_PATH)

print("\nFiltering focused rows...")
focused_df = df[df["focused?"] == 1]

print("Number of focused samples:", len(focused_df))

X = focused_df.drop(columns=["focused?"])
probs = model.predict_proba(X)

# Probability of class 1 (focused)
focused_index = int(np.where(model.classes_ == 1)[0][0])
p_focused = probs[:, focused_index]

print("\nStatistics for focused rows:")
print("Mean P(focused):", p_focused.mean())
print("Min  P(focused):", p_focused.min())
print("Max  P(focused):", p_focused.max())

# How many did it correctly classify?
correct = (p_focused >= 0.5).sum()
print("Correct classifications:", correct, "/", len(p_focused))
print("Accuracy on focused samples:", correct / len(p_focused))
