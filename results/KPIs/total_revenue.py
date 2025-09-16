import s3_methods
import os
import pandas as pd
import logging
from extract_store import load_csv_as_df

def generate_kpi():
    """
    Calculate total revenue from the sales data CSV.
    """
    csv_path = "results/csvs_in/revenue_total.csv"
    if not os.path.exists(csv_path):
        logging.error(f"CSV file not found: {csv_path}")
        return None

    try:
        df = load_csv_as_df(csv_path)
        total_rev = df['total_revenue'].sum()
        logging.info(f"Total Revenue: {total_rev}")
        return total_rev
    except Exception as e:
        logging.error(f"Error calculating total revenue: {e}")
        return None

