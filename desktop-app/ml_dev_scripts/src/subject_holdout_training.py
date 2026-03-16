from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import joblib
import matplotlib
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = BASE_DIR.parent / "RF" / "data" / "master_dataset.csv"
DEFAULT_OUTPUT_DIR = BASE_DIR / "docs" / "subject_holdout"

TARGET_COLUMN = "label"
SUBJECT_COLUMN = "subject_id"

ABSOLUTE_FEATURES = [
    "face_x",
    "face_y",
    "face_w",
    "face_h",
    "left_eye_x",
    "left_eye_y",
    "left_eye_w",
    "left_eye_h",
    "right_eye_x",
    "right_eye_y",
    "right_eye_w",
    "right_eye_h",
]

RELATIVE_FEATURES = [
    "left_eye_dx",
    "left_eye_dy",
    "right_eye_dx",
    "right_eye_dy",
    "sym_dx",
    "sym_dy",
    "yaw",
    "pitch",
    "roll",
]


@dataclass
class FoldMetrics:
    model_type: str
    feature_set: str
    test_subject: int
    train_subjects: str
    train_rows: int
    test_rows: int
    accuracy: float
    precision: float
    recall: float
    f1: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train subject holdout models on master_dataset.csv."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help=f"Path to the dataset CSV. Default: {DEFAULT_DATASET_PATH}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for trained models and metrics. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Validation split fraction taken from the training subjects for XGBoost early stopping.",
    )
    return parser.parse_args()


def load_dataset(dataset_path: Path, feature_columns: list[str]) -> pd.DataFrame:
    df = pd.read_csv(dataset_path)
    required_columns = set(feature_columns) | {TARGET_COLUMN, SUBJECT_COLUMN}
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    cleaned = df.dropna(subset=list(required_columns)).copy()
    cleaned[TARGET_COLUMN] = cleaned[TARGET_COLUMN].astype(int)
    cleaned[SUBJECT_COLUMN] = cleaned[SUBJECT_COLUMN].astype(int)
    return cleaned


def build_rf_model() -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=1,
    )


def build_xgb_model() -> xgb.XGBClassifier:
    return xgb.XGBClassifier(
        objective="binary:logistic",
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
        n_jobs=1,
        early_stopping_rounds=20,
    )


def save_rf_model(
    model: RandomForestClassifier,
    output_dir: Path,
    feature_columns: list[str],
    feature_set_name: str,
    test_subject: int,
    train_subjects: list[int],
) -> None:
    model_path = output_dir / f"rf_{feature_set_name}_subject_{test_subject}.joblib"
    joblib.dump(
        {
            "model": model,
            "feature_columns": feature_columns,
            "model_type": "rf",
            "feature_set": feature_set_name,
            "train_subjects": train_subjects,
            "test_subject": test_subject,
        },
        model_path,
    )


def save_xgb_model(
    model: xgb.XGBClassifier,
    output_dir: Path,
    feature_columns: list[str],
    feature_set_name: str,
    test_subject: int,
    train_subjects: list[int],
) -> None:
    model_path = output_dir / f"xgb_{feature_set_name}_subject_{test_subject}.json"
    metadata_path = output_dir / f"xgb_{feature_set_name}_subject_{test_subject}.metadata.json"
    model.save_model(model_path)
    metadata_path.write_text(
        json.dumps(
            {
                "feature_columns": feature_columns,
                "model_type": "xgb",
                "feature_set": feature_set_name,
                "train_subjects": train_subjects,
                "test_subject": test_subject,
            },
            indent=2,
        )
    )


def save_confusion_matrix(
    *,
    y_true: pd.Series,
    y_pred: pd.Series,
    output_dir: Path,
    model_type: str,
    feature_set_name: str,
    test_subject: int,
) -> None:
    matrix = confusion_matrix(y_true, y_pred)
    labels = ["0", "1"]

    matrix_df = pd.DataFrame(
        matrix,
        index=[f"actual_{label}" for label in labels],
        columns=[f"predicted_{label}" for label in labels],
    )
    matrix_df.to_csv(
        output_dir / f"{model_type}_{feature_set_name}_subject_{test_subject}_confusion_matrix.csv"
    )

    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("Actual label")
    ax.set_title(f"{model_type.upper()} {feature_set_name} - Subject {test_subject}")

    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            ax.text(col, row, str(matrix[row, col]), ha="center", va="center", color="black")

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(
        output_dir / f"{model_type}_{feature_set_name}_subject_{test_subject}_confusion_matrix.png"
    )
    plt.close(fig)
    print(
        f"\nConfusion matrix for {model_type.upper()} {feature_set_name} "
        f"(test subject {test_subject}):"
    )
    print(matrix_df.to_string())


def train_rf_fold(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_columns: list[str],
    output_dir: Path,
    feature_set_name: str,
    test_subject: int,
    train_subjects: list[int],
) -> tuple[pd.Series, FoldMetrics]:
    X_train = train_df[feature_columns]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[feature_columns]
    y_test = test_df[TARGET_COLUMN]

    model = build_rf_model()
    model.fit(X_train, y_train)
    predictions = pd.Series(model.predict(X_test), index=test_df.index)

    save_rf_model(model, output_dir, feature_columns, feature_set_name, test_subject, train_subjects)
    save_confusion_matrix(
        y_true=y_test,
        y_pred=predictions,
        output_dir=output_dir,
        model_type="rf",
        feature_set_name=feature_set_name,
        test_subject=test_subject,
    )

    metrics = FoldMetrics(
        model_type="rf",
        feature_set=feature_set_name,
        test_subject=test_subject,
        train_subjects=",".join(map(str, train_subjects)),
        train_rows=len(train_df),
        test_rows=len(test_df),
        accuracy=accuracy_score(y_test, predictions),
        precision=precision_score(y_test, predictions, zero_division=0),
        recall=recall_score(y_test, predictions, zero_division=0),
        f1=f1_score(y_test, predictions, zero_division=0),
    )
    return predictions, metrics


def train_xgb_fold(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_columns: list[str],
    output_dir: Path,
    feature_set_name: str,
    test_subject: int,
    train_subjects: list[int],
    validation_fraction: float,
) -> tuple[pd.Series, FoldMetrics]:
    X_train = train_df[feature_columns]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[feature_columns]
    y_test = test_df[TARGET_COLUMN]

    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train,
        y_train,
        test_size=validation_fraction,
        random_state=42,
        stratify=y_train,
    )

    model = build_xgb_model()
    model.fit(X_fit, y_fit, eval_set=[(X_val, y_val)], verbose=False)
    predictions = pd.Series(model.predict(X_test), index=test_df.index)

    save_xgb_model(model, output_dir, feature_columns, feature_set_name, test_subject, train_subjects)
    save_confusion_matrix(
        y_true=y_test,
        y_pred=predictions,
        output_dir=output_dir,
        model_type="xgb",
        feature_set_name=feature_set_name,
        test_subject=test_subject,
    )

    metrics = FoldMetrics(
        model_type="xgb",
        feature_set=feature_set_name,
        test_subject=test_subject,
        train_subjects=",".join(map(str, train_subjects)),
        train_rows=len(train_df),
        test_rows=len(test_df),
        accuracy=accuracy_score(y_test, predictions),
        precision=precision_score(y_test, predictions, zero_division=0),
        recall=recall_score(y_test, predictions, zero_division=0),
        f1=f1_score(y_test, predictions, zero_division=0),
    )
    return predictions, metrics


def run_subject_holdout(
    *,
    model_type: str,
    feature_set_name: str,
    feature_columns: list[str],
    dataset_path: Path,
    output_dir: Path,
    validation_fraction: float,
) -> None:
    df = load_dataset(dataset_path, feature_columns)
    subjects = sorted(df[SUBJECT_COLUMN].unique().tolist())
    if len(subjects) < 2:
        raise ValueError("Need at least two subjects to run subject holdout training.")

    variant_output_dir = output_dir / f"{model_type}_{feature_set_name}"
    variant_output_dir.mkdir(parents=True, exist_ok=True)

    trainer: Callable[..., tuple[pd.Series, FoldMetrics]]
    if model_type == "rf":
        trainer = train_rf_fold
    elif model_type == "xgb":
        trainer = train_xgb_fold
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    fold_metrics: list[FoldMetrics] = []

    for test_subject in subjects:
        train_subjects = [subject for subject in subjects if subject != test_subject]
        train_df = df[df[SUBJECT_COLUMN].isin(train_subjects)]
        test_df = df[df[SUBJECT_COLUMN] == test_subject]

        if model_type == "xgb":
            _, metrics = trainer(
                train_df,
                test_df,
                feature_columns,
                variant_output_dir,
                feature_set_name,
                test_subject,
                train_subjects,
                validation_fraction,
            )
        else:
            _, metrics = trainer(
                train_df,
                test_df,
                feature_columns,
                variant_output_dir,
                feature_set_name,
                test_subject,
                train_subjects,
            )

        fold_metrics.append(metrics)
        print(
            f"[{model_type.upper()} {feature_set_name}] "
            f"train={metrics.train_subjects} test={metrics.test_subject} "
            f"acc={metrics.accuracy:.4f} f1={metrics.f1:.4f}"
        , flush=True)

    metrics_df = pd.DataFrame(asdict(metric) for metric in fold_metrics)
    metrics_df.to_csv(variant_output_dir / "fold_metrics.csv", index=False)

    summary = {
        "model_type": model_type,
        "feature_set": feature_set_name,
        "dataset_path": str(dataset_path.resolve()),
        "subjects": subjects,
        "feature_columns": feature_columns,
        "fold_count": len(fold_metrics),
        "mean_accuracy": float(metrics_df["accuracy"].mean()),
        "mean_precision": float(metrics_df["precision"].mean()),
        "mean_recall": float(metrics_df["recall"].mean()),
        "mean_f1": float(metrics_df["f1"].mean()),
    }
    (variant_output_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    print(f"\nSaved outputs to {variant_output_dir}")
    print(metrics_df.to_string(index=False))
    print(
        "\nAverage metrics: "
        f"accuracy={summary['mean_accuracy']:.4f}, "
        f"precision={summary['mean_precision']:.4f}, "
        f"recall={summary['mean_recall']:.4f}, "
        f"f1={summary['mean_f1']:.4f}"
    )
