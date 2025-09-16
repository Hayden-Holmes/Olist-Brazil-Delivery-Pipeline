import logging, numpy as np
logger = logging.getLogger(__name__)

# --------------------
# Column Existence
# --------------------
def product_columns_exist(df, ref):
    """All expected product/seller columns are present."""
    missing = set(ref["expected_product_seller_cols"]) - set(df.columns)
    return [] if not missing else [f"Missing columns: {sorted(missing)}"]

# --------------------
# Basic Sanity Checks
# --------------------
def product_non_negative(df, ref=None):
    """Ensure key numeric fields are not negative."""
    errors = []
    for col in ["avg_price","avg_freight","orders_per_product",
                "avg_review_score","orders_fulfilled","avg_ship_days"]:
        negatives = df[df[col] < 0]
        if len(negatives) > 1000:
            errors.append(f"{col} has {len(negatives)} negative values")
    return errors

def product_avg_review_bounds(df, ref=None):
    """Check review scores are within 1–5."""
    out = df[(df["avg_review_score"] < 1) | (df["avg_review_score"] > 5)]
    return [] if out.empty else [f"{len(out)} avg_review_score outside [1,5]"]

def product_ship_days_reasonable(df, ref=None):
    """Check avg_ship_days is within a practical window (0–60 days)."""
    out = df[(df["avg_ship_days"] < 0) | (df["avg_ship_days"] > 60)]
    return [] if len(out) < 1000 else [f"{len(out)} avg_ship_days outside [0,60]"]

def product_price_freight_ratio(df, ref=None):
    """
    Check that avg_freight is not wildly larger than avg_price.
    We allow freight to be up to twice the price as a sanity bound.
    """
    out = df[(df["avg_price"] > 0) &
             (df["avg_freight"] / df["avg_price"] > 2)]
    return [] if len(out) < 1000 else [f"{len(out)} products with freight/price ratio > 2"]

# --------------------
# Reference Consistency
# --------------------
def product_order_totals(df, ref):
    """
    Check that global order counts roughly match reference
    (sum of orders_per_product should be close to total_orders).
    """
    total_orders_est = df["orders_per_product"].sum()
    expected = ref["total_orders"]
    # allow 10% margin because one order can contain many products
    if abs(total_orders_est - expected) > expected * 0.1:
        return [f"Estimated orders {total_orders_est} far from expected {expected}"]
    return []

# --------------------
# Runner
# --------------------
def run_all_expectations(df, ref):
    checks = [
        product_columns_exist,
        product_non_negative,
        product_avg_review_bounds,
        product_ship_days_reasonable,
        product_price_freight_ratio,
    ]
    errors = []
    for c in checks:
        logger.info("Running %s", c.__name__)
        errors.extend(c(df, ref))
    return errors
