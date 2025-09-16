from pre_proccess import train_churn_model
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import logging
from matplot.report_matrix import graphs_for_LR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def logistic_regression_model(csv_path: str, save_path: str):
    # Train model
    logger.info("Training logistic regression model...")
    results = train_churn_model(csv_path, model="logistic_regression")
    pipeline = results["pipeline"]
    X_train = results["X_train"]
    y_train = results["y_train"]
    X_test = results["X_test"]
    y_test = results["y_test"]
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
    report = {"classification": classification_report(y_test, y_pred), "confusion_matrix": confusion_matrix(y_test, y_pred)}
    logger.info("Classification Report:\n %s", report)

    # Save model
    model_dir = Path(save_path  / "models")
    model_dir.mkdir(parents=True, exist_ok=True)
    # replace any file that has "logistic_regression.*timestamp*" in its name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = model_dir / f"logistic_regression_{timestamp}.joblib"
    if model_dir.glob(f"logistic_regression_*.joblib"):
        for file in model_dir.glob(f"logistic_regression_*.joblib"):
            logger.info(f"Removing old model file: {file}")
            file.unlink()
    joblib.dump(pipeline, model_path)
    logger.info(f"Model saved to {model_path}")

    #save info to csv
    csv_dir = Path(save_path / "csvs")
    csv_dir.mkdir(parents=True, exist_ok=True)
    # Get feature names after preprocessing
    feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()

    # Match coefficients to feature names
    coef_df = pd.DataFrame({
        "feature": feature_names,
        "coefficient": pipeline.named_steps['classifier'].coef_[0]  # binary classification
    })
    results_df = pd.DataFrame([{
        "timestamp": timestamp,
        "model": "logistic_regression",
        "classification_report": report["classification"].replace("\n", " | "),
        "confusion_matrix": report["confusion_matrix"].tolist(),
        "coefficients": coef_df.to_dict(orient="records")
    }])

    results_df.to_csv(csv_dir / "logistic_regression_results.csv", index=False)
    logger.info(f"Results appended to {csv_dir / 'logistic_regression_results.csv'}")
    # Generate graphs
    



if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[2]  # directory of the script being run
    CSV_PATH = BASE_DIR / "csvs_in" / "ML_churn_features.csv"
    csv_path = CSV_PATH
    save_path = BASE_DIR / "ML"
    logistic_regression_model(csv_path, save_path)
