# src/data.py
import pandas as pd
from .config import RAW_DATA_PATH, TARGET_COLUMN, EXPECTED_COLUMNS
from .utils import print_section


def load_raw_data(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw focus dataset from a tab-separated file."""
    print_section(f"Loading data from {path}")

    # Your file uses TABs between columns, not commas
    df = pd.read_csv(path, sep="\t")

    # Optional sanity check on columns
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing expected columns in CSV: {missing_cols}\n"
            f"Actual columns I see: {list(df.columns)}"
        )

    print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
    return df


def preprocess_data(df: pd.DataFrame):
    """
    Preprocess the dataset:
    - Convert 'focused?' to binary 0/1
    - Drop 'timestamp' (not useful as a feature for this classification)
    - Drop rows with missing values
    """
    print_section("Preprocessing data")

    # Convert focused? to binary
    target_col = TARGET_COLUMN
    df[target_col] = (
        df[target_col]
        .astype(str)
        .str.strip()
        .str.upper()
        .map({"TRUE": 1, "FALSE": 0, "1": 1, "0": 0})
    )

    if df[target_col].isna().any():
        raise ValueError(
            f"Target column '{target_col}' has values that couldn't be mapped to 0/1."
        )

    # Drop timestamp if present
    if "timestamp" in df.columns:
        df = df.drop(columns=["timestamp"])

    # Drop rows with any missing values
    before = len(df)
    df = df.dropna()
    after = len(df)
    if after < before:
        print(f"Dropped {before - after} rows with missing values.")

    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]

    print(f"Final feature columns: {list(X.columns)}")
    print(f"Dataset size after cleaning: {len(X)} rows")
    print(f"Class balance:\n{y.value_counts()}")

    return X, y


def load_and_prepare_data(path: str = RAW_DATA_PATH):
    """Convenience function: load CSV and return X, y."""
    df = load_raw_data(path)
    X, y = preprocess_data(df)
    return X, y