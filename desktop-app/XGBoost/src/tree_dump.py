import joblib
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "focus_xgb_pipeline.joblib")


pipeline = joblib.load(MODEL_PATH)

xgb_model = pipeline.named_steps["model"]
preprocessor = pipeline.named_steps["preprocessor"]
feature_names = preprocessor.get_feature_names_out()

booster = xgb_model.get_booster()

booster.feature_names = list(feature_names)
print(booster.get_dump(with_stats=True, dump_format="text")[0])
