from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    balanced_accuracy_score, confusion_matrix, roc_auc_score
)
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import xgboost as xgb
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

df = pd.read_csv(
    "C:\\Uni Tests, Assignments, Labs\\Capstone Project\\Manual Collection Dataset\\master_dataset.csv"
)
df = df.sort_values(["subject_id"]).reset_index(drop=True)

# DERIVED EYE FEATURES
df["left_eye_ear"] = df["left_eye_h"] / (df["left_eye_w"] + 1e-6)
df["right_eye_ear"] = df["right_eye_h"] / (df["right_eye_w"] + 1e-6)
df["eye_ear_mean"] = (df["left_eye_ear"] + df["right_eye_ear"]) / 2

# Relative eye positions (centered on face)
df["left_eye_dx_center"] = df["left_eye_x"] - (df["face_x"] + df["face_w"]/2)
df["left_eye_dy_center"] = df["left_eye_y"] - (df["face_y"] + df["face_h"]/2)
df["right_eye_dx_center"] = df["right_eye_x"] - (df["face_x"] + df["face_w"]/2)
df["right_eye_dy_center"] = df["right_eye_y"] - (df["face_y"] + df["face_h"]/2)

# Symmetry features
df["sym_dx"] = df["right_eye_dx_center"] - df["left_eye_dx_center"]
df["sym_dy"] = df["right_eye_dy_center"] - df["left_eye_dy_center"]

feature_cols = [
    "eye_ear_mean",
    "left_eye_dx_center", "left_eye_dy_center",
    "right_eye_dx_center", "right_eye_dy_center",
    "yaw", "pitch", "roll",
    "sym_dx", "sym_dy"
]

target_col = "label"
subjects = df["subject_id"].unique()

os.makedirs("results", exist_ok=True)
metrics_file = "results/loso_metrics_pruned.csv"
fi_file = "results/feature_importances_pruned.csv"
log_file = "results/training_log_pruned.txt"
open(log_file, "w").close()


def log(message):
    print(message)
    with open(log_file, "a") as f:
        f.write(str(message) + "\n")


all_metrics = []
fi_all = []

for test_subject in subjects:
    log(f"\n===== Testing on Subject {test_subject} =====")

    train_df = df[df['subject_id'] != test_subject]
    test_df = df[df['subject_id'] == test_subject]

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]

    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    # Compute class imbalance ratio
    n_focused = sum(y_train == 1)
    n_distracted = sum(y_train == 0)
    scale_pos_weight = n_focused / n_distracted
    log(
        f"Training class ratio (Focused / Distracted): {n_focused} / {n_distracted}")
    log(f"Using scale_pos_weight = {scale_pos_weight:.2f}")

    # Train/validation split
    X_train_inner, X_val, y_train_inner, y_val = train_test_split(
        X_train, y_train, test_size=0.2, stratify=y_train, random_state=42
    )

    # XGBoost parameter search
    param_grid = {
        "max_depth": [3, 4, 5],
        "learning_rate": [0.01, 0.03, 0.05],
        "n_estimators": [200, 300, 400],
        "subsample": [0.7, 0.8, 0.9],
        "colsample_bytree": [0.7, 0.8, 0.9],
        "gamma": [0, 0.1, 0.2],
        "min_child_weight": [1, 3, 5]
    }

    base_model = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        tree_method="hist",
        n_jobs=-1,
        scale_pos_weight=scale_pos_weight
    )

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
        n_iter=20,
        scoring="f1",
        cv=3,
        verbose=1,
        n_jobs=-1,
        random_state=42
    )

    search.fit(X_train_inner, y_train_inner)
    best_model = search.best_estimator_
    log(f"Best parameters: {search.best_params_}")
    best_model.save_model(
        f"results/xgb_model_subject_{test_subject}_pruned.json")

    # Optimize threshold for distracted class (0)
    y_val_prob = best_model.predict_proba(X_val)[:, 1]
    best_f1 = 0
    best_thresh = 0.5
    for thresh in np.arange(0.1, 0.91, 0.01):
        y_val_pred = (y_val_prob > thresh).astype(int)
        f1 = f1_score(y_val, y_val_pred, pos_label=0, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh

    log(
        f"Best threshold (max F1 Distracted) on validation: {best_thresh:.2f} (F1={best_f1:.4f})")

    # Evaluate on test set
    y_prob = best_model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob > best_thresh).astype(int)

    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)
    precision_d = precision_score(y_test, y_pred, pos_label=0, zero_division=0)
    recall_d = recall_score(y_test, y_pred, pos_label=0, zero_division=0)
    f1_d = f1_score(y_test, y_pred, pos_label=0, zero_division=0)
    precision_f = precision_score(y_test, y_pred, pos_label=1, zero_division=0)
    recall_f = recall_score(y_test, y_pred, pos_label=1, zero_division=0)
    f1_f = f1_score(y_test, y_pred, pos_label=1, zero_division=0)
    auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)

    log("Confusion Matrix:")
    log(cm)

    metrics_row = {
        "Test_Subject": test_subject,
        "Accuracy": acc,
        "Balanced_Accuracy": bal_acc,
        "AUC": auc,
        "Precision_Distracted": precision_d,
        "Recall_Distracted": recall_d,
        "F1_Distracted": f1_d,
        "Precision_Focused": precision_f,
        "Recall_Focused": recall_f,
        "F1_Focused": f1_f,
        "TN": cm[0, 0],
        "FP": cm[0, 1],
        "FN": cm[1, 0],
        "TP": cm[1, 1],
        "Threshold": best_thresh
    }
    all_metrics.append(metrics_row)

    pred_df = test_df.copy()
    pred_df["prediction"] = y_pred
    pred_df["probability"] = y_prob
    pred_df.to_csv(
        f"results/predictions_subject_{test_subject}_pruned.csv", index=False)

    importance = best_model.feature_importances_
    fi = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": importance,
        "Test_Subject": test_subject
    })
    fi_all.append(fi)

    # Plot feature importance
    plt.figure(figsize=(8, 6))
    sorted_idx = np.argsort(importance)
    plt.barh(np.array(feature_cols)[sorted_idx], importance[sorted_idx])
    plt.title(f"Feature Importance - Subject {test_subject}")
    plt.tight_layout()
    plt.savefig(
        f"results/feature_importance_subject_{test_subject}_pruned.png")
    plt.close()

# Save metrics
metrics_df = pd.DataFrame(all_metrics)
metrics_df.to_csv(metrics_file, index=False)

fi_df = pd.concat(fi_all, ignore_index=True)
fi_df.to_csv(fi_file, index=False)

log("\n===== FINAL RESULTS =====")
log(metrics_df)
log(f"\nAverage Accuracy: {metrics_df['Accuracy'].mean():.4f}")
log(f"Average Balanced Accuracy: {metrics_df['Balanced_Accuracy'].mean():.4f}")
log(f"Average AUC: {metrics_df['AUC'].mean():.4f}")
log(f"Average F1 (Distracted): {metrics_df['F1_Distracted'].mean():.4f}")
log(f"Average F1 (Focused): {metrics_df['F1_Focused'].mean():.4f}")
