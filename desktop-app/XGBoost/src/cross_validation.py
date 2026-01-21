import json
from sklearn.model_selection import StratifiedKFold, cross_validate, cross_val_predict
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from .config import RANDOM_STATE
from .data import load_and_prepare_data
from .model import build_pipeline
from .utils import print_section, ensure_dir

REPORT_DIR = "docs"


def evaluate_model():
    X, y = load_and_prepare_data("XGBoost/data/raw/raw_coordinates.csv")

    print_section("CROSS-VALIDATION CONFIGURATION")
    n_splits = 5
    print(f"Using StratifiedKFold with {n_splits} folds.")

    skf = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    pipeline = build_pipeline(X.columns)

    print_section("RUNNING CROSS-VALIDATION")
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

    y_pred_cv = cross_val_predict(
        build_pipeline(X.columns),
        X,
        y,
        cv=skf,
        n_jobs=-1
    )

    results_summary = {}
    for metric in scoring:
        scores = cv_results[f"test_{metric}"]
        results_summary[metric] = {
            "mean": scores.mean(),
            "std": scores.std(),
            "all_folds": scores.tolist()
        }

    overall_acc = accuracy_score(y, y_pred_cv)
    results_summary["overall_accuracy"] = overall_acc
    results_summary["classification_report"] = classification_report(
        y, y_pred_cv, output_dict=True)
    results_summary["confusion_matrix"] = confusion_matrix(
        y, y_pred_cv).tolist()

    print("\nCross-validation results (mean ± std across folds):\n")
    for metric in scoring:
        print(
            f"{metric.capitalize():<10}: {results_summary[metric]['mean']:.4f} ± {results_summary[metric]['std']:.4f}")
    print("\nOverall Accuracy:", overall_acc)
    print("\nClassification Report:\n", classification_report(y, y_pred_cv))
    print("\nConfusion Matrix:\n", confusion_matrix(y, y_pred_cv))

    ensure_dir(REPORT_DIR)
    report_path = f"{REPORT_DIR}/cv_results.json"
    with open(report_path, "w") as f:
        json.dump(results_summary, f, indent=4)
    print_section("CROSS-VALIDATION RESULTS SAVED")
    print(f"Saved CV report at: {report_path}")


if __name__ == "__main__":
    evaluate_model()
