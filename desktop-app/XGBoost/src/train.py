# src/train.py
import os
import joblib

from sklearn.model_selection import StratifiedKFold, cross_validate, cross_val_predict
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from .config import (
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

    # 2. Announce and configure cross-validation
    print_section("CROSS-VALIDATION ENABLED")
    n_splits = 5
    print(f"Using StratifiedKFold cross-validation with {n_splits} folds.")
    print("Each fold will train on 80% of the data and validate on 20%,")
    print("cycling through all possible folds to evaluate the model robustly.")

    skf = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    # 3. Build pipeline for cross-validation
    pipeline = build_pipeline(X.columns)

    # 4. Run cross-validation
    print_section("RUNNING CROSS-VALIDATION (this may take a moment)")
    scoring = ["accuracy", "precision", "recall", "f1"]

    cv_results = cross_validate(
        pipeline,
        X,
        y,
        cv=skf,
        scoring=scoring,
        return_train_score=False,
        n_jobs=-1,
    )

    print("\nCross-validation results (mean ± std across all folds):\n")
    for metric in scoring:
        scores = cv_results[f"test_{metric}"]
        print(f"  {metric.capitalize():<10}: {scores.mean():.4f} ± {scores.std():.4f}")

    # 5. Out-of-fold predictions for a detailed evaluation
    print_section("CROSS-VALIDATED PREDICTIONS (combined from all folds)")
    y_pred_cv = cross_val_predict(
        build_pipeline(X.columns),
        X,
        y,
        cv=skf,
        n_jobs=-1,
    )

    overall_acc = accuracy_score(y, y_pred_cv)
    print(f"Overall Accuracy (from CV predictions): {overall_acc:.4f}\n")

    print("Classification Report (based on CV predictions):")
    print(classification_report(y, y_pred_cv))

    print("Confusion Matrix (based on CV predictions):")
    print(confusion_matrix(y, y_pred_cv))

    # 6. Train final model on all data
    print_section("TRAINING FINAL MODEL ON FULL DATASET")
    final_pipeline = build_pipeline(X.columns)
    final_pipeline.fit(X, y)

    # 7. Save the final trained model
    ensure_dir(MODEL_DIR)
    joblib.dump(final_pipeline, MODEL_PATH)

    print_section("MODEL SAVED SUCCESSFULLY")
    print(f"Model stored at: {MODEL_PATH}")
    print("\nNOTE:")
    print("This model was trained AFTER cross-validation on the full dataset.")
    print("Cross-validation was used ONLY to evaluate performance,")
    print("not to generate the final model file.\n")