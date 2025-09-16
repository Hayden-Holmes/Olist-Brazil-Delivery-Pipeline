import logging
from KPIs.total_revenue import generate_kpi
import extract_store


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
   extract_store.exd_new()
   # extract_store.exd_key("ML_churn_features.csv","queries/ML/churn_features.sql")