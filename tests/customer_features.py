# ============================================================
# Customer-Level Feature Expectations
# ============================================================
import logging

# reference_values.py
import pandas as pd



logger = logging.getLogger(__name__)

def columns_exist(df, ref):
    missing = set(ref["expected_customer_cols"]) - set(df.columns)
    return [] if not missing else [f"Expected: {ref['expected_customer_cols']}, got: {list(df.columns)}"]

def customer_count_matches(df, ref):
    actual, expected = len(df), ref["total_customers"]
    return [] if actual == expected else [f"Customer count {actual} != {expected}"]

def total_orders_sum_matches(df, ref):
    actual, expected = int(df["total_orders"].sum()), ref["total_orders"]
    return [] if actual == expected else [f"total_orders sum {actual} != {expected}"]

def total_spent_sum_matches(df, ref):
    actual = round(df["total_spent"].sum(), 2)
    expected = round(ref["total_revenue"], 2)
    return [] if abs(actual - expected) <= 1e-4 else [f"total_spent sum {actual} != {expected}"]

def avg_order_value_consistency(df, ref=None):
    errors = []
    
    for idx, r in df.iterrows():
        if r["total_orders"] > 0:
            exp = r["total_spent"]/r["total_orders"]
            if abs(r["avg_order_value"] - exp) > 1e-6:
                errors.append(f"{r['customer_unique_id']} AOV mismatch")

                
    if errors:
        return [f"{len(errors)} rows with avg_order_value inconsistency: {errors[:5]}..."]
    return []

def tenure_within_span(df, ref):
    span = ref["dataset_span_days"]
    invalid = df[df["tenure_days"] > span + 1e-6]
    return [] if invalid.empty else [f"{len(invalid)} rows have tenure_days > dataset span {span}"]

def numeric_non_negative(df, ref=None):
    cols = ["total_orders","total_spent","avg_order_value",
            "avg_items_per_order","avg_installments","tenure_days"]
    errors = []
    for c in cols:
        if c in df.columns:
            neg = df[df[c] < 0]
            if not neg.empty:
                errors.append(f"{c} has {len(neg)} negative values")
    return errors

def run_all_expectations(df, ref):
    checks = [
        columns_exist, customer_count_matches,
        total_orders_sum_matches, total_spent_sum_matches,
        avg_order_value_consistency, tenure_within_span,
        numeric_non_negative
    ]
    errs=[]
    for c in checks:
        logger.info("Running %s", c.__name__)
        errs.extend(c(df, ref))
    return errs
