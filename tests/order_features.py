import logging, numpy as np
import pandas as pd
logger = logging.getLogger(__name__)

def columns_exist(df, ref):
    missing = set(ref["expected_order_cols"]) - set(df.columns)
    return [] if not missing else [f"Missing columns: {sorted(missing)}"]

def order_count_matches(df, ref):
    actual, expected = len(df), ref["total_orders"]
    return [] if actual == expected else [f"Order count {actual} != {expected}"]

def order_items_value_sum(df, ref):
    # Check that total order_items_value approximates payment total
    logger.info("Converting order_items_value to numeric: %s", df.head())
    try:
        df["order_items_value"] = pd.to_numeric(df["order_items_value"], errors='coerce')
    except Exception as e:
        logger.error("Error converting order_items_value: %s", e)
        return [f"Error converting order_items_value: {e}"]
    actual = round(df["order_items_value"].sum(), 2)
    expected = round(ref["total_gross_revenue"], 2)
    if abs(actual - expected) > expected*0.1:  # allow 10% gap for freight
        return [f"Items value sum {actual} far from revenue {expected}"]
    return []

def freight_ratio_bounds(df, ref=None):
    outliers = df[(df["freight_ratio"] < 0) | (df["freight_ratio"] > 2)]
    print(df["freight_ratio"].describe())
    if len(outliers) > 500:
        return [f"freight_ratio has {len(outliers)} outliers"]
    return []

def timing_non_negative(df, ref=None):
    cols = ["hours_to_approval","days_to_carrier","days_carrier_to_customer"]
    errs=[]
    for c in cols:
        neg = df[df[c] < 0]
        if len(neg) > 1500:
            errs.append(f"{c} has {len(neg)} negative values")
    return errs

def run_all_expectations(df, ref):
    checks = [
        columns_exist, order_count_matches, order_items_value_sum,
        freight_ratio_bounds, timing_non_negative
    ]
    errs=[]
    for c in checks:
        logger.info("Running %s", c.__name__)
        errs.extend(c(df, ref))
    return errs
