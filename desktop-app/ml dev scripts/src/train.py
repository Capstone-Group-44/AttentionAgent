from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
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
    'right_eye_dx', 'right_eye_dy', 'sym_dx', 'sym_dy', 'yaw', 'pitch', 'roll'
]

target_col = 'label'
subjects = df['subject_id'].unique()

os.makedirs("results", exist_ok=True)
metrics_file = "results/loso_metrics.txt"
fi_file = "results/feature_importances.csv"

with open(metrics_file, "w") as f:
    f.write("Test_Subject\tAccuracy\tPrecision\tRecall\tF1\n")

fi_all = []

for test_subject in subjects:
    print(f"\n===== Testing on Subject {test_subject} =====")

    train_df = df[df['subject_id'] != test_subject]
    test_df = df[df['subject_id'] == test_subject]

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]

    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    X_train_inner, X_val, y_train_inner, y_val = train_test_split(
        X_train, y_train,
        test_size=0.2,
        stratify=y_train,
        random_state=42
    )

    # Convert to DMatrix (required for xgb.train)
    dtrain = xgb.DMatrix(X_train_inner, label=y_train_inner)
    dval = xgb.DMatrix(X_val, label=y_val)
    dtest = xgb.DMatrix(X_test, label=y_test)

    params = {
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "seed": 42
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

    y_pred = (bst.predict(dtest) > 0.5).astype(int)
    bst.save_model(f"results/xgb_model_subject_{test_subject}.json")

    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label=0, zero_division=0)
    recall = recall_score(y_test, y_pred, pos_label=0, zero_division=0)
    f1 = f1_score(y_test, y_pred, pos_label=0, zero_division=0)

    print(
        f"Accuracy: {acc:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

    with open(metrics_file, "a") as f:
        f.write(
            f"{test_subject}\t{acc:.4f}\t{precision:.4f}\t{recall:.4f}\t{f1:.4f}\n")

    fi = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": bst.get_score(importance_type='weight').values(),
        "Test_Subject": test_subject
    })

    # Some features may be missing if not used in splits
    if len(fi) < len(feature_cols):
        missing = set(feature_cols) - set(fi["Feature"])
        for m in missing:
            fi = pd.concat([fi, pd.DataFrame(
                {"Feature": [m], "Importance": [0], "Test_Subject": [test_subject]})])
    fi_all.append(fi)

    # Plot feature importances
    plt.figure(figsize=(8, 6))
    xgb.plot_importance(bst, importance_type='weight', height=0.6)
    plt.title(f"Feature Importances - Subject {test_subject}")
    plt.tight_layout()
    plt.savefig(f"results/feature_importance_subject_{test_subject}.png")
    plt.close()

fi_df = pd.concat(fi_all, ignore_index=True)
fi_df.to_csv(fi_file, index=False)

metrics_df = pd.read_csv(metrics_file, sep="\t")
print("\nPer Subject Results:")
print(metrics_df)
print("\nAverage Accuracy:", metrics_df["Accuracy"].mean())
print("Average Precision:", metrics_df["Precision"].mean())
print("Average Recall:", metrics_df["Recall"].mean())
print("Average F1:", metrics_df["F1"].mean())
