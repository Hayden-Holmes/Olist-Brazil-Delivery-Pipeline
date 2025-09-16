import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast
from pathlib import Path
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



graph_dir = Path("results/ML/matplot/graphs/Linear_Regression")

def graph_report(report: pd.DataFrame, model:str, save_path:Path):
    # Paths
    graph_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. Classification Report (Table) ---

    plt.figure(figsize=(6, 3))
    sns.heatmap(report.set_index(report.columns[0])[["precision", "recall", "f1-score"]], 
                annot=True, fmt=".2f", cmap="Blues")
    plt.title("Classification Report")
    plt.tight_layout()
    plt.savefig(Path(save_path / model / "classification_report.png"))
    logger.info(f"Classification report graph saved as {save_path / model / 'classification_report.png'}")
    plt.close()


def graph_confusion_matrix(matrix: pd.DataFrame, model:str, save_path:Path):
    # --- 2. Confusion Matrix (Heatmap) ---

    plt.figure(figsize=(4, 3))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(Path(save_path / model / "confusion_matrix.png"))
    logger.info(f"Confusion matrix graph saved as {save_path / model / 'confusion_matrix.png'}")
    plt.close()


def graph_coefficients(coeffs: pd.DataFrame, model:str, save_path:Path):
    # --- 3. Coefficients (Bar Graph) ---
  
    plt.figure(figsize=(8, 6))
    if model == "random_forest":
        sns.barplot(x="feature", y="importance", 
                data=coeffs.sort_values(by="importance"), palette="viridis", hue="importance")
        plt.title("Random Forest Feature Importances")
    else:
        sns.barplot(x="coefficient", y="feature", 
                    data=coeffs.sort_values(by="coefficient"), palette="coolwarm", hue="coefficient")
        plt.title("Logistic Regression Coefficients")
    
    plt.tight_layout()
    plt.savefig(Path(save_path / model / "coefficients.png"))
    logger.info(f"Coefficients graph saved as {save_path / model / 'coefficients.png'}")
    plt.close()
    
def graphs_for_LR():
    # Read CSV
    logger.info("Starting graphs for Logistic Regression...")
    Path("results/ML/logistic_regression").mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(Path("results/ML/csvs/logistic_regression_results.csv"))

    #parse the classification report from string to dataframe
    report_str = df.loc[0, "classification_report"]

    #remove macro avg and weighted avg rows from the report string
    logger.info(f"Raw classification report string: {report_str}")
    rows = [r.split() for r in report_str.split("|") if r.strip()]
    class_rows = [r for r in rows if r[0] not in ["macro", "weighted", "accuracy"]]
    class_columns = class_rows[0]
    class_columns.insert(0, "class")
    logger.info(f"Filtered classification report rows: {class_rows}")
    logger.info("columns: " + str(class_columns))
    # First row is headers
    try:
        header = ["class","precision", "recall", "f1-score", "support"]
        if len(class_rows[0]) != len(header):
            raise ValueError("Header length mismatch")
        report_df = pd.DataFrame(class_rows[1:], columns=class_rows[0])
    except Exception as e:
        logger.error(f"Error parsing classification report: {e}")
        return

    # Convert numeric cols
    for col in ["precision", "recall", "f1-score", "support"]:
        logger.info(f"Converting column {col} to numeric")
        report_df[col] = pd.to_numeric(report_df[col], errors="coerce")

    # Parse confusion matrix from string to dataframe
    cm = ast.literal_eval(df.loc[0, "confusion_matrix"])  # safe parsing
    cm_df = pd.DataFrame(cm, index=["Actual 0", "Actual 1"], columns=["Pred 0", "Pred 1"])

   # Parse coefficients from string to dataframe
    coeffs = ast.literal_eval(df.loc[0, "coefficients"])  # parse string → list of dicts
    coef_df = pd.DataFrame(coeffs)
   # Generate graphs
    graph_report(report_df, model="logistic_regression", save_path=Path("results/ML"))
    graph_confusion_matrix(cm_df, model="logistic_regression", save_path=Path("results/ML"))
    graph_coefficients(coef_df, model="logistic_regression", save_path=Path("results/ML"))

def graphs_for_RF():
    logger.info("Starting graphs for Random Forest...")
    #make directory if not exists
    Path("results/ML/random_forest").mkdir(parents=True, exist_ok=True)
    # Read CSV
    df = pd.read_csv(Path("results/ML/csvs/random_forest_results.csv"))
    if df.empty:
        logger.error("Random Forest results CSV is empty.")
        return
    #parse the classification report from string to dataframe
    report_str = df.loc[0, "classification_report"]
    logger.info(f"Raw classification report string: {report_str}")
    rows = [r.split() for r in report_str.split("|") if r.strip()]
    class_rows = [r for r in rows if r[0] not in ["macro", "weighted", "accuracy"]]
    class_columns = class_rows[0]
    class_columns.insert(0, "class")
    logger.info(f"Filtered classification report rows: {class_rows}")
    logger.info("columns: " + str(class_columns))
    # First row is headers
    try:
        header = ["class","precision", "recall", "f1-score", "support"]
        if len(class_rows[0]) != len(header):
            raise ValueError("Header length mismatch")
        report_df = pd.DataFrame(class_rows[1:], columns=class_rows[0])
    except Exception as e:
        logger.error(f"Error parsing classification report: {e}")
        return
    # Convert numeric cols
    for col in ["precision", "recall", "f1-score", "support"]:
        logger.info(f"Converting column {col} to numeric")
        report_df[col] = pd.to_numeric(report_df[col], errors="coerce")
    # Parse confusion matrix from string to dataframe
    cm = ast.literal_eval(df.loc[0, "confusion_matrix"])  # safe
    cm_df = pd.DataFrame(cm, index=["Actual 0", "Actual 1"], columns=["Pred 0", "Pred 1"])
    
    # Parse feature importances from string to dataframe
    importances = ast.literal_eval(df.loc[0, "feature_importances"])  #
    importances_df = pd.DataFrame(importances)
    # Convert feature_importance to numeric
    logging.info("feature importances: " + str(importances_df))
    # Generate graphs
    graph_report(report_df, model="random_forest", save_path=Path("results/ML"))
    graph_confusion_matrix(cm_df, model="random_forest", save_path=Path("results/ML"))
    graph_coefficients(importances_df, model="random_forest", save_path=Path("results/ML"))

if __name__ == "__main__":
    graphs_for_LR()
    graphs_for_RF()