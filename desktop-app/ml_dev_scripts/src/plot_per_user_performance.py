from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_METRICS_ROOT = BASE_DIR / "docs" / "subject_holdout"
DEFAULT_OUTPUT_PATH = BASE_DIR / "docs" / "per_user_performance_f1.png"

VARIANTS = [
    ("rf_relative", "RF Relative", "#4C78A8"),
    ("xgb_relative", "XGB Relative", "#E45756"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a per-user F1 comparison chart for relative-feature models."
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


def load_data(metrics_root: Path) -> pd.DataFrame:
    frames = []
    for folder_name, label, _color in VARIANTS:
        metrics_path = metrics_root / folder_name / "fold_metrics.csv"
        if not metrics_path.exists():
            raise FileNotFoundError(f"Missing metrics file: {metrics_path}")

        df = pd.read_csv(metrics_path)
        frames.append(
            pd.DataFrame(
                {
                    "test_subject": df["test_subject"].astype(int),
                    "f1": df["f1"].astype(float),
                    "variant": label,
                }
            )
        )
    return pd.concat(frames, ignore_index=True).sort_values(["test_subject", "variant"])


def plot_chart(chart_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subjects = sorted(chart_df["test_subject"].unique().tolist())
    x = list(range(len(subjects)))
    width = 0.34

    fig, ax = plt.subplots(figsize=(10, 6))

    for idx, (_folder, label, color) in enumerate(VARIANTS):
        subset = (
            chart_df[chart_df["variant"] == label]
            .sort_values("test_subject")
            .reset_index(drop=True)
        )
        offsets = [value + (-width / 2 if idx == 0 else width / 2) for value in x]
        bars = ax.bar(offsets, subset["f1"], width=width, label=label, color=color)

        for bar, value in zip(bars, subset["f1"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.015,
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    ax.set_title("Per-User Performance", fontsize=16, weight="bold")
    ax.set_xlabel("Test Subject", fontsize=12)
    ax.set_ylabel("F1 Score", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([str(subject) for subject in subjects])
    ax.set_ylim(0.0, 1.0)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    chart_df = load_data(args.metrics_root)
    plot_chart(chart_df, args.output)

    print("Per-user F1 values:")
    print(chart_df.to_string(index=False))
    print(f"\nSaved chart to: {args.output}")


if __name__ == "__main__":
    main()
