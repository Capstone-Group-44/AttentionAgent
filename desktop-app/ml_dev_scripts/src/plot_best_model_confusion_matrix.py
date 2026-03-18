from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_METRICS_DIR = BASE_DIR / "docs" / "subject_holdout" / "xgb_relative"
DEFAULT_OUTPUT_PATH = BASE_DIR / "docs" / "best_model_confusion_matrix.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an aggregate confusion matrix for the best model across all held-out subjects."
    )
    parser.add_argument(
        "--metrics-dir",
        type=Path,
        default=DEFAULT_METRICS_DIR,
        help=f"Folder containing per-subject confusion matrices. Default: {DEFAULT_METRICS_DIR}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output image path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    return parser.parse_args()


def load_aggregate_confusion_matrix(metrics_dir: Path) -> pd.DataFrame:
    csv_paths = sorted(metrics_dir.glob("*_confusion_matrix.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No confusion matrix CSV files found in {metrics_dir}")

    total = None
    for csv_path in csv_paths:
        matrix_df = pd.read_csv(csv_path, index_col=0)
        total = matrix_df if total is None else total.add(matrix_df, fill_value=0)

    return total.astype(int)


def plot_matrix(matrix_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(matrix_df.values, cmap="Blues")

    ax.set_xticks(range(len(matrix_df.columns)))
    ax.set_yticks(range(len(matrix_df.index)))
    ax.set_xticklabels(matrix_df.columns)
    ax.set_yticklabels(matrix_df.index)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("Actual label")
    ax.set_title("Best Model Confusion Matrix (XGB Relative)", fontsize=15, weight="bold")

    for row in range(matrix_df.shape[0]):
        for col in range(matrix_df.shape[1]):
            ax.text(
                col,
                row,
                str(matrix_df.iat[row, col]),
                ha="center",
                va="center",
                fontsize=12,
                color="black",
            )

    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    matrix_df = load_aggregate_confusion_matrix(args.metrics_dir)
    plot_matrix(matrix_df, args.output)

    print("Aggregate confusion matrix for XGB Relative:")
    print(matrix_df.to_string())
    print(f"\nSaved chart to: {args.output}")


if __name__ == "__main__":
    main()
