import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_churn_model(csv_path: str, model: str, features:dict=None):
    # Define features
    categorical_features = ["customer_state"]
    numeric_features = [
        "total_orders", "total_spent", "avg_order_value",
        "distinct_products", "frequency", "recency"
    ]
    
    # --- Load Data ---
    logger.info(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)

    

    # Drop identifier
    df = df.drop(columns=["customer_id"])
    required_columns = categorical_features + numeric_features + [ "churned"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing columns in data: {missing_columns}")
        raise ValueError(f"Missing columns in data: {missing_columns}")

    # Features and target
    X = df.drop(columns=["churned"])
    y = df["churned"].astype(int)  # Ensure target is integer type

    # Define column types
    categorical_features = [] #"customer_state" - dropped

    #NOTE dropped recency - similar calculations as churned
    numeric_features = [
        "total_orders", "total_spent", "avg_order_value",
        "distinct_products", "frequency"
    ]

    # --- Preprocessing ---
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", StandardScaler(), numeric_features)
        ]
    )

    # --- Split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    # --- Model Training ---
    if model not in ["logistic_regression", "random_forest"]:
        logger.error("Model must be 'logistic_regression' or 'random_forest'")
        raise ValueError("Model must be 'logistic_regression' or 'random_forest'")

    if model == "logistic_regression":
        # Logistic Regression Pipeline
        logger.info("Setting up Logistic Regression pipeline")
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
        ])
        logger.info("Logistic Regression pipeline created")
        return {
            "pipeline": pipeline,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }
    

    # --- Random Forest Pipeline ---
    if model == "random_forest":
        logger.info("Setting up Random Forest pipeline")
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"))
        ])
        logger.info("Random Forest pipeline created")
        return {
            "pipeline": pipeline,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }

