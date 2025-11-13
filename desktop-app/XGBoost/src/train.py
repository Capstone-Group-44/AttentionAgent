# src/train.py
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .config import (
    TEST_SIZE,
    RANDOM_STATE,
    MODEL_DIR,
    MODEL_PATH,
)
from .data import load_and_prepare_data
from .model import build_pipeline
from .utils import ensure_dir, print_section


def train_model():
    # 1. Load and prepare data
    X, y = load_and_prepare_data()

    # 2. Train/test split
    print_section("Train/Test Split")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # 3. Build pipeline
    pipeline = build_pipeline(X.columns)

    # 4. Train
    print_section("Training XGBoost model")
    pipeline.fit(X_train, y_train)

    # 5. Evaluate
    print_section("Evaluating on test set")
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}\n")

    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # 6. Save model
    ensure_dir(MODEL_DIR)
    joblib.dump(pipeline, MODEL_PATH)
    print_section("Model Saved")
    print(f"Saved trained pipeline to: {MODEL_PATH}")