# src/predict.py
import joblib
import pandas as pd
from typing import Dict, List, Union

from .config import MODEL_PATH
from .utils import print_section


def load_trained_model(model_path: str = MODEL_PATH):
    print_section(f"Loading trained model from {model_path}")
    model = joblib.load(model_path)
    return model


def make_input_dataframe(
    samples: List[Dict[str, Union[int, float]]], expected_columns: List[str]
) -> pd.DataFrame:
    """
    Convert a list of dicts into a DataFrame with consistent column ordering.
    """
    df = pd.DataFrame(samples)

    # Ensure columns exist
    missing = [c for c in expected_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns for prediction: {missing}")

    # Only keep expected columns and in the same order
    df = df[expected_columns]
    return df


def predict_focus(
    samples: List[Dict[str, Union[int, float]]],
    model_path: str = MODEL_PATH,
):
    """
    Predict focus / not focus for a batch of samples.

    Each sample dict should contain these keys:
    - screen_width
    - screen_height
    - left_gaze_x
    - left_gaze_y
    - right_gaze_x
    - right_gaze_y
    - face_x
    - face_y
    - face_z
    (no 'timestamp', no 'focused?')
    """
    model = load_trained_model(model_path)

    # Get feature names from the pipeline's preprocessor
    # We stored all numeric features directly, so we can infer from the trained pipeline.
    preprocessor = model.named_steps["preprocessor"]
    feature_names = preprocessor.transformers_[0][2]  # ("num", scaler, [cols...])

    df = make_input_dataframe(samples, feature_names)

    print_section("Running Predictions")
    preds = model.predict(df)
    probs = model.predict_proba(df)[:, 1]  # probability of focused = 1

    results = []
    for sample, pred, prob in zip(samples, preds, probs):
        results.append(
            {
                "input": sample,
                "focused_prediction": bool(pred),
                "focused_probability": float(prob),
            }
        )

    return results


# Example usage for manual testing:
if __name__ == "__main__":
    # Example: one frame of data
    example_sample = {
        "screen_width": 1512,
        "screen_height": 982,
        "left_gaze_x": 617.79,
        "left_gaze_y": 445.99,
        "right_gaze_x": 792.61,
        "right_gaze_y": 466.45,
        "face_x": 690.8,
        "face_y": 542.3,
        "face_z": -0.0612,
    }

    results = predict_focus([example_sample])
    for r in results:
        print(r)