from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    balanced_accuracy_score, confusion_matrix,
    classification_report, roc_auc_score
)
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

df = pd.read_csv(
    "C:\\Uni Tests, Assignments, Labs\\Capstone Project\\Manual Collection Dataset\\master_dataset.csv")

feature_cols = [
    'face_x', 'face_y', 'face_w', 'face_h',
    'left_eye_x', 'left_eye_y', 'left_eye_w', 'left_eye_h',
    'right_eye_x', 'right_eye_y', 'right_eye_w', 'right_eye_h',
    'left_eye_dx', 'left_eye_dy',
    'right_eye_dx', 'right_eye_dy', 'sym_dx', 'sym_dy',
    'yaw', 'pitch', 'roll'
]

target_col = 'label'
subjects = df['subject_id'].unique()

os.makedirs("results", exist_ok=True)

metrics_file = "results/loso_metrics_smote.csv"
fi_file = "results/feature_importances_smote.csv"
log_file = "results/training_log_smote.txt"

open(log_file, "w").close()


def log(message):
    print(message)
    with open(log_file, "a") as f:
        f.write(str(message) + "\n")


all_metrics = []
fi_all = []

smote = SMOTE(sampling_strategy='auto', random_state=42)

for test_subject in subjects:

    log(f"\n===== Testing on Subject {test_subject} =====")

    train_df = df[df['subject_id'] != test_subject]
    test_df = df[df['subject_id'] == test_subject]

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]

    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    X_train_inner, X_val, y_train_inner, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.2,
        stratify=y_train,
        random_state=42
    )

    #  SMOTE Oversampling
    X_train_bal, y_train_bal = smote.fit_resample(X_train_inner, y_train_inner)
    log(f"Training set size before SMOTE: {X_train_inner.shape[0]}")
    log(f"Training set size after SMOTE: {X_train_bal.shape[0]}")

    n_focused = (y_train_bal == 1).sum()
    n_distracted = (y_train_bal == 0).sum()
    scale_pos_weight = n_focused / n_distracted
    log(
        f"Balanced training class ratio (Focused / Distracted): {n_focused}/{n_distracted}")
    log(f"XGBoost scale_pos_weight: {scale_pos_weight:.2f}")

    dtrain = xgb.DMatrix(X_train_bal, label=y_train_bal)
    dval = xgb.DMatrix(X_val, label=y_val)
    dtest = xgb.DMatrix(X_test, label=y_test)

    params = {
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "seed": 42,
        "scale_pos_weight": 1
    }

    evals = [(dtrain, "train"), (dval, "val")]

    bst = xgb.train(
        params,
        dtrain,
        num_boost_round=1000,
        evals=evals,
        early_stopping_rounds=10,
        verbose_eval=True
    )

    bst.save_model(f"results/xgb_model_subject_{test_subject}_smote.json")

    y_val_prob = bst.predict(dval)
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

    y_prob = bst.predict(dtest)
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
        f"results/predictions_subject_{test_subject}_smote.csv", index=False)

    score_dict = bst.get_score(importance_type='weight')
    fi = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": [score_dict.get(f, 0) for f in feature_cols],
        "Test_Subject": test_subject
    })
    fi_all.append(fi)

    plt.figure(figsize=(8, 6))
    xgb.plot_importance(bst, importance_type='weight', height=0.6)
    plt.title(f"Feature Importances - Subject {test_subject}")
    plt.tight_layout()
    plt.savefig(f"results/feature_importance_subject_{test_subject}_smote.png")
    plt.close()

metrics_df = pd.DataFrame(all_metrics)
metrics_df.to_csv(metrics_file, index=False)
fi_df = pd.concat(fi_all, ignore_index=True)
fi_df.to_csv(fi_file, index=False)

log("\n===== FINAL RESULTS =====")
log(metrics_df)

log("\nAverage Accuracy: " + str(metrics_df["Accuracy"].mean()))
log("Average Balanced Accuracy: " +
    str(metrics_df["Balanced_Accuracy"].mean()))
log("Average AUC: " + str(metrics_df["AUC"].mean()))
log("Average F1 (Distracted): " + str(metrics_df["F1_Distracted"].mean()))
log("Average F1 (Focused): " + str(metrics_df["F1_Focused"].mean()))
