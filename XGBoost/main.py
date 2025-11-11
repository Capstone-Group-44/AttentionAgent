# main.py
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import matplotlib.pyplot as plt

# 1. Paths
DATA_PATH = os.path.join("data", "raw", "eye_data.csv")

def load_data(path: str):
    df = pd.read_csv(path)

    # Separate features and target
    X = df.drop(columns=["is_looking"])
    y = df["is_looking"]

    return X, y

def train_test_split_data(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)

def build_model():
    """
    Basic XGBoost binary classifier.
    You can tune these hyperparameters later.
    """
    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",   # good default for CPU
        random_state=42
    )
    return model

def plot_feature_importance(model, feature_names):
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]

    plt.figure()
    plt.title("Feature Importance")
    plt.bar(range(len(feature_names)), importance[indices])
    plt.xticks(range(len(feature_names)), np.array(feature_names)[indices], rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def main():
    # 2. Load data
    X, y = load_data(DATA_PATH)
    print("Loaded data with shape:", X.shape, "Target shape:", y.shape)

    # 3. Train-test split
    X_train, X_test, y_train, y_test = train_test_split_data(X, y)

    # 4. Build model
    model = build_model()

    # 5. Fit model
    print("Training XGBoost model...")
    model.fit(X_train, y_train)

    # 6. Evaluate on test set
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {acc:.4f}\n")

    print("Classification report:")
    print(classification_report(y_test, y_pred))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    # 7. Feature importance
    plot_feature_importance(model, X.columns)

    # 8. Save model (optional)
    import joblib
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, os.path.join("models", "xgb_eye_model.joblib"))
    print("Model saved to models/xgb_eye_model.joblib")

if __name__ == "__main__":
    main()