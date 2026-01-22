import joblib
from .config import MODEL_DIR, MODEL_PATH
from .data import load_and_prepare_data
from .model import build_pipeline
from .utils import ensure_dir, print_section


def train_final_model():

    X, y = load_and_prepare_data()

    print_section("TRAINING MODEL ON FULL DATASET")
    final_pipeline = build_pipeline(X.columns)
    final_pipeline.fit(X, y)

    ensure_dir(MODEL_DIR)
    joblib.dump(final_pipeline, MODEL_PATH)
    print_section("MODEL SAVED SUCCESSFULLY")
    print(f"Model stored at: {MODEL_PATH}")
    print("\nNOTE: This final model was trained AFTER cross-validation evaluation.")


if __name__ == "__main__":
    train_final_model()
