# delivery_prediction_with_flags.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)

# ---------- 1. Load Data ----------
df = pd.read_csv("results/csvs_in/orders_curated.csv")

# ---------- 2. Target ----------
logging.info("Creating target variable 'late_delivery'")
df["late_delivery"] = (df["days_est_vs_actual"] > 0).astype(int)

# ---------- 3. Data Cleaning (optional) ----------
logging.info("Applying outlier flags to clean data")
df = df.query("freight_ratio_outlier == 0 and neg_days_to_carrier == 0 and neg_days_carrier_to_customer == 0")

# ---------- 4. Features ----------
base_features = [
    "hours_to_approval","days_to_carrier",
    "order_items_value","freight_value","freight_ratio",
    "distinct_sellers","distinct_products","total_items","max_installments"
]



X = df[base_features].fillna(0)
y = df["late_delivery"]

# ---------- 5. Split ----------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

logging.info(f"Training samples: {X_train.shape[0]}, Testing samples: {X_test.shape[0]}")
# ---------- 6. Train XGBoost ----------
model = XGBClassifier(
    n_estimators=300, max_depth=6, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
    random_state=42
)
model.fit(X_train, y_train)

# ---------- 7. Evaluate ----------
pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:,1]
logging.info("Accuracy: %f", accuracy_score(y_test, pred))
logging.info("ROC AUC: %f", roc_auc_score(y_test, prob))
logging.info("\nClassification Report:\n%s", classification_report(y_test, pred))

# ---------- 8. Feature Importance ----------
feat_imp = pd.Series(model.feature_importances_, index=base_features).sort_values()
plt.figure(figsize=(8,6))
feat_imp.plot(kind="barh")
plt.title("Feature Importance with Outlier Flags")
plt.tight_layout()
plt.savefig("results/delivery_prediciton/feature_importance.png")
plt.show()
