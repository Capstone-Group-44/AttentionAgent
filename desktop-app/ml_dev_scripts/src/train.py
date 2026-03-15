from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    balanced_accuracy_score, confusion_matrix,
    roc_auc_score
)
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import xgboost as xgb
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from imblearn.combine import SMOTETomek

matplotlib.use("Agg")

df = pd.read_csv(
    "C:\\Uni Tests, Assignments, Labs\\Capstone Project\\Manual Collection Dataset\\master_dataset.csv"
)

df = df.sort_values(["subject_id"]).reset_index(drop=True)

# TEMPORAL FEATURE ENGINEERING
# Head movement velocity
df["yaw_vel"] = df.groupby("subject_id")["yaw"].diff().fillna(0)
df["pitch_vel"] = df.groupby("subject_id")["pitch"].diff().fillna(0)
df["roll_vel"] = df.groupby("subject_id")["roll"].diff().fillna(0)

# Eye motion magnitude
df["left_eye_motion"] = np.sqrt(df["left_eye_dx"]**2 + df["left_eye_dy"]**2)
df["right_eye_motion"] = np.sqrt(df["right_eye_dx"]**2 + df["right_eye_dy"]**2)

# Short temporal stability (rolling window)
df["yaw_std_5"] = (
    df.groupby("subject_id")["yaw"]
    .rolling(5)
    .std()
    .reset_index(level=0, drop=True)
    .fillna(0)
)

df["pitch_std_5"] = (
    df.groupby("subject_id")["pitch"]
    .rolling(5)
    .std()
    .reset_index(level=0, drop=True)
    .fillna(0)
)

df["eye_motion_mean_5"] = (
    df.groupby("subject_id")["left_eye_motion"]
    .rolling(5)
    .mean()
    .reset_index(level=0, drop=True)
    .fillna(0)
)

feature_cols = [
    'face_x', 'face_y', 'face_w', 'face_h',

    'left_eye_x', 'left_eye_y', 'left_eye_w', 'left_eye_h',
    'right_eye_x', 'right_eye_y', 'right_eye_w', 'right_eye_h',

    'left_eye_dx', 'left_eye_dy',
    'right_eye_dx', 'right_eye_dy',

    'sym_dx', 'sym_dy',

    'yaw', 'pitch', 'roll',

    # TEMPORAL FEATURES
    'yaw_vel', 'pitch_vel', 'roll_vel',
    'left_eye_motion', 'right_eye_motion',
    'yaw_std_5', 'pitch_std_5',
    'eye_motion_mean_5'
]

target_col = 'label'
subjects = df['subject_id'].unique()

os.makedirs("results", exist_ok=True)

metrics_file = "results/loso_metrics_tuned.csv"
fi_file = "results/feature_importances_tuned.csv"
log_file = "results/training_log_tuned.txt"

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

    X_train_inner, X_val, y_train_inner, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.2,
        stratify=y_train,
        random_state=42
    )

    log(f"Training set size before SMOTE: {len(X_train_inner)}")

    smt = SMOTETomek(random_state=42)

    X_train_inner_res, y_train_inner_res = smt.fit_resample(
        X_train_inner, y_train_inner
    )

    log(f"Training set size after SMOTE: {len(X_train_inner_res)}")

    log(
        f"Balanced training class ratio (Focused / Distracted): "
        f"{sum(y_train_inner_res==1)}/{sum(y_train_inner_res==0)}"
    )

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
        n_jobs=-1
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

    search.fit(X_train_inner_res, y_train_inner_res)

    best_model = search.best_estimator_

    log(f"Best parameters: {search.best_params_}")

    best_model.save_model(
        f"results/xgb_model_subject_{test_subject}_tuned.json"
    )

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
        f"Best threshold (max F1 Distracted) on validation: "
        f"{best_thresh:.2f} (F1={best_f1:.4f})"
    )

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
        f"results/predictions_subject_{test_subject}_tuned.csv",
        index=False
    )

    importance = best_model.feature_importances_

    fi = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": importance,
        "Test_Subject": test_subject
    })

    fi_all.append(fi)

    plt.figure(figsize=(8, 6))

    sorted_idx = np.argsort(importance)

    plt.barh(
        np.array(feature_cols)[sorted_idx],
        importance[sorted_idx]
    )

    plt.title(f"Feature Importance - Subject {test_subject}")

    plt.tight_layout()

    plt.savefig(
        f"results/feature_importance_subject_{test_subject}_tuned.png"
    )

    plt.close()

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
