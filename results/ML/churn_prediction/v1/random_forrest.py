from pre_proccess import train_churn_model
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def random_forest_model(csv_path: str, save_path: str):
    # Train model
    logger.info("Training random forest model...")
    results = train_churn_model(csv_path, model="random_forest")
    pipeline = results["pipeline"]
    X_train = results["X_train"]
    y_train = results["y_train"]
    X_test  = results["X_test"]
    y_test  = results["y_test"]

    logger.info("Preview of training data:\n%s", pd.DataFrame(X_train).head())
    logger.info("Preview of training churn:\n%s", pd.DataFrame(y_train).head())

    try:
        pipeline.fit(X_train, y_train)
    except Exception as e:
        logger.error("Error occurred while training the model: %s", e)
        return

    # Predictions
    y_pred = pipeline.predict(X_test)

    # Evaluation
    report = {
        "classification": classification_report(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred)
    }
    logger.info("Classification Report:\n %s", report)

    # Save model (overwrite any previous RF model, keep a timestamped one)
    model_dir = Path(save_path / "models")
    model_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # remove any existing RF models to keep a single historical file, like your LR flow
    for file in model_dir.glob("random_forest_*.joblib"):
        logger.info(f"Removing old model file: {file}")
        file.unlink()

    model_path = model_dir / f"random_forest_{timestamp}.joblib"
    joblib.dump(pipeline, model_path)
    logger.info(f"Model saved to {model_path}")

    # ----- Save results (CSV) -----
    csv_dir = Path(save_path / "csvs")
    csv_dir.mkdir(parents=True, exist_ok=True)

    # Feature importances mapped to transformed feature names
    feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
    clf = pipeline.named_steps["classifier"]

    # Guard: some sklearn versions may not have feature_importances_ until fitted
    try:
        importances = clf.feature_importances_
    except AttributeError:
        logger.error("Classifier has no feature_importances_.")
        importances = []

    if len(importances) != len(feature_names):
        logger.warning(
            "Length mismatch: %d importances vs %d features",
            len(importances), len(feature_names)
        )

    importances_df = pd.DataFrame({
        "feature": feature_names[:len(importances)],
        "importance": importances
    }).sort_values("importance", ascending=False)

    results_df = pd.DataFrame([{
        "timestamp": timestamp,
        "model": "random_forest",
        "classification_report": report["classification"].replace("\n", " | "),
        "confusion_matrix": report["confusion_matrix"].tolist(),
        "feature_importances": importances_df.to_dict(orient="records")
    }])

    results_df.to_csv(csv_dir / "random_forest_results.csv", index=False)
    logger.info(f"Results saved to {csv_dir / 'random_forest_results.csv'}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[2]
    CSV_PATH = BASE_DIR / "csvs_in" / "ML_churn_features.csv"
    SAVE_PATH = BASE_DIR / "ML"
    random_forest_model(CSV_PATH, SAVE_PATH)
