from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_METRICS_ROOT = BASE_DIR / "docs" / "subject_holdout"
DEFAULT_OUTPUT_PATH = BASE_DIR / "docs" / "metrics_comparison_grouped.png"

VARIANTS = [
    ("rf_absolute", "RF Absolute"),
    ("rf_relative", "RF Relative"),
    ("xgb_absolute", "XGB Absolute"),
    ("xgb_relative", "XGB Relative"),
]

METRIC_COLUMNS = ["precision", "recall", "f1"]
METRIC_COLORS = ["#4C78A8", "#72B7B2", "#E45756"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a grouped bar chart for precision, recall, and F1 across model variants."
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


def load_metrics(metrics_root: Path) -> pd.DataFrame:
    rows = []
    for folder_name, display_name in VARIANTS:
        metrics_path = metrics_root / folder_name / "fold_metrics.csv"
        if not metrics_path.exists():
            raise FileNotFoundError(f"Missing metrics file: {metrics_path}")

        df = pd.read_csv(metrics_path)
        rows.append(
            {
                "variant": display_name,
                "precision": df["precision"].mean(),
                "recall": df["recall"].mean(),
                "f1": df["f1"].mean(),
            }
        )
    return pd.DataFrame(rows)


def plot_chart(chart_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    x = np.arange(len(chart_df))
    width = 0.23

    fig, ax = plt.subplots(figsize=(11, 6))

    for idx, metric_name in enumerate(METRIC_COLUMNS):
        offsets = x + (idx - 1) * width
        bars = ax.bar(
            offsets,
            chart_df[metric_name],
            width=width,
            label=metric_name.capitalize(),
            color=METRIC_COLORS[idx],
        )
        for bar, value in zip(bars, chart_df[metric_name]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.012,
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_title("Precision / Recall / F1 Comparison", fontsize=16, weight="bold")
    ax.set_xlabel("Model + Feature Type", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(chart_df["variant"])
    ax.set_ylim(0.0, 1.0)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    chart_df = load_metrics(args.metrics_root)
    plot_chart(chart_df, args.output)

    print("Mean precision/recall/F1 comparison:")
    print(chart_df.to_string(index=False))
    print(f"\nSaved chart to: {args.output}")


if __name__ == "__main__":
    main()
