from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_METRICS_ROOT = BASE_DIR / "docs" / "subject_holdout"
DEFAULT_OUTPUT_PATH = BASE_DIR / "docs" / "model_feature_comparison_f1.png"

VARIANTS = [
    ("rf_absolute", "RF Absolute"),
    ("rf_relative", "RF Relative"),
    ("xgb_absolute", "XGB Absolute"),
    ("xgb_relative", "XGB Relative"),
]

COLORS = ["#4C78A8", "#72B7B2", "#F58518", "#E45756"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a bar chart comparing mean F1 across model/feature variants."
    )
    parser.add_argument(
        "--metrics-root",
        type=Path,
        default=DEFAULT_METRICS_ROOT,
        help=f"Root folder containing variant fold_metrics.csv files. Default: {DEFAULT_METRICS_ROOT}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output image path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    return parser.parse_args()


def load_variant_f1(metrics_root: Path) -> pd.DataFrame:
    rows = []
    for folder_name, display_name in VARIANTS:
        metrics_path = metrics_root / folder_name / "fold_metrics.csv"
        if not metrics_path.exists():
            raise FileNotFoundError(f"Missing metrics file: {metrics_path}")

        df = pd.read_csv(metrics_path)
        rows.append(
            {
                "variant": display_name,
                "mean_f1": df["f1"].mean(),
            }
        )
    return pd.DataFrame(rows)


def plot_comparison(chart_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(chart_df["variant"], chart_df["mean_f1"], color=COLORS, width=0.65)

    ax.set_title("Model + Feature Comparison", fontsize=16, weight="bold")
    ax.set_xlabel("Model + Feature Type", fontsize=12)
    ax.set_ylabel("Mean F1 Score", fontsize=12)
    ax.set_ylim(0.0, 1.0)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, chart_df["mean_f1"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.015,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=11,
            weight="bold",
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    chart_df = load_variant_f1(args.metrics_root)
    plot_comparison(chart_df, args.output)

    print("Mean F1 comparison:")
    print(chart_df.to_string(index=False))
    print(f"\nSaved chart to: {args.output}")


if __name__ == "__main__":
    main()
