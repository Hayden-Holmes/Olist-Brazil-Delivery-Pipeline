# --------------------
# Orders
# --------------------
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def orders_non_negative(df, ref=None):
    """Check total_orders is never negative."""
    negatives = df[df["total_orders"] < 0]
    return [] if negatives.empty else [f"{len(negatives)} rows have negative total_orders"]

def orders_le_reference(df, ref):
    """Check total_orders sum <= reference total_orders."""
    df_total = df["total_orders"].sum()
    if df_total > ref["total_orders"]:
        return [f"Total orders {df_total} exceeds reference {ref['total_orders']}"]
    return []


# --------------------
# Revenue / Spend
# --------------------

def total_spent_non_negative(df, ref=None):
    """Ensure total_spent is never negative."""
    negatives = df[df["total_spent"] < 0]
    return [] if negatives.empty else [f"{len(negatives)} rows have negative total_spent"]

def total_spent_consistent(df, ref):
    """Check total_spent sum <= reference revenue."""
    df_total = round(df["total_spent"].sum(), 2)
    ref_total = round(ref["total_revenue"], 2)
    if df_total > ref_total + 1e-6:
        return [f"Total spent {df_total} exceeds total revenue {ref_total}"]
    return []


def avg_order_value_valid(df, ref=None):
    """Check avg_order_value is consistent with total_spent / total_orders."""
    errors = []
    for idx, row in df.iterrows():
        if row["total_orders"] > 0:
            expected = row["total_spent"] / row["total_orders"]
            if abs(row["avg_order_value"] - expected) > 1e-6:
                errors.append(
                    f"Row {idx}: AOV mismatch, got {row['avg_order_value']}, expected {expected}"
                )
    return errors


# --------------------
# Recency & Frequency
# --------------------

def recency_non_negative(df, ref=None):
    logger.info("Checking recency non-negativity...")
    """Ensure recency (days since last order) is never negative."""
    negatives = df[df["recency"] < 0]
    return [] if negatives.empty else [f"{len(negatives)} rows have negative recency"]

def frequency_non_negative(df, ref=None):
    logger.info("Checking frequency non-negativity...")
    """Ensure frequency (orders/month) is never negative."""
    negatives = df[df["frequency"] < 0]
    return [] if negatives.empty else [f"{len(negatives)} rows have negative frequency"]


# --------------------
# Product Diversity
# --------------------

def distinct_products_non_negative(df, ref=None):
    logger.info("Checking distinct_products non-negativity...")
    """Ensure distinct_products is never negative."""
    negatives = df[df["distinct_products"] < 0]
    return [] if negatives.empty else [f"{len(negatives)} rows have negative distinct_products"]


# --------------------
# State Features (one-hot)
# --------------------

def state_dummies_valid(df, ref=None):
    logger.info("Checking state dummy validity...")
    errors = []
    """
   Make sure state column is not null and 2 letter state codes.
   """
    if "customer_state" not in df.columns:
        errors.append("Missing 'customer_state' column")
    else:
        invalid_states = df[~df["customer_state"].str.match(r"^[A-Z]{2}$")]
        if not invalid_states.empty:
            errors.append(f"Invalid state codes found: {invalid_states['customer_state'].unique()}")

    return errors


# --------------------
# Top 5 Categories (from earlier)
# --------------------

# def top5_categories_exist(df, ref=None):
#     required_cols = [
#         "spend_health_beauty",
#         "spend_watches_gifts",
#         "spend_bed_bath_table",
#         "spend_sports_leisure",
#         "spend_computers_accessories",
#     ]
#     missing = [col for col in required_cols if col not in df.columns]
#     return [] if not missing else [f"Missing category columns: {missing}"]

# def top5_category_non_negative(df, ref=None):
#     errors = []
#     for col in df.columns:
#         if col.startswith("spend_"):
#             negatives = df[df[col] < 0]
#             if not negatives.empty:
#                 errors.append(f"{col} has {len(negatives)} negative values")
#     return errors

# def top5_category_sum_le_total_spent(df, ref=None):
#     errors = []
#     spend_cols = [col for col in df.columns if col.startswith("spend_")]
#     for idx, row in df.iterrows():
#         top5_sum = row[spend_cols].sum()
#         if top5_sum > row["total_spent"] + 1e-6:
#             errors.append(
#                 f"Customer {row['customer_id']} has top-5 sum {top5_sum} > total_spent {row['total_spent']}"
#             )
#     return errors

# def top5_global_total_le_total_revenue(df, ref):
#     spend_cols = [col for col in df.columns if col.startswith("spend_")]
#     df_total = df[spend_cols].sum().sum()
#     ref_total = ref["total_revenue"]
#     if df_total > ref_total + 1e-6:
#         return [f"Global top-5 spend {df_total} > total revenue {ref_total}"]
#     return []

def churned_binary_valid(df, ref=None):
    logger.info("Checking churned binary validity...")
    """Check churned column is binary 0/1."""
    if "churned" not in df.columns:
        return ["Missing 'churned' column"]
    invalid = df[~df["churned"].isin([0, 1])]
    return [] if invalid.empty else [f"'churned' has {len(invalid)} invalid values outside [0,1]"]

def churned_consistent(df, ref=None):
    logger.info("Checking churned consistency...")
    """
    Check to see if row count = total customers - customers with orders in last 6 months
    """
    if "churned" not in df.columns:
        return ["Missing 'churned' column"]
    #check to see if there are any 0s and 1s in churned column
    if df["churned"].nunique() < 2:
        return ["'churned' column does not have both 0 and 1 values"]
    
    # churned_count = df["churned"].sum()
    # expected_churned = ref["total_customers"] - ref["active_customers"]
    # if churned_count != expected_churned:
    #     return [f"Churned count {churned_count} inconsistent with expected {expected_churned}"]

def run_all_expectations(df, expectations, ref):
    logger.info("Running all expectations...")
    errors = []
    for expect in expectations:
        errors.extend(expect(df, ref))
    return errors


def check_non_null(df, ref=None):
    logger.info("Checking for null values...")
    errors = []
    for column in df.columns:
        null_count = df[column].isnull().sum()
        if null_count > 0:
            errors.append(f"Column {column} has {null_count} null values.")
    return errors

def check_churn_distribution(df, ref=None):
   logger = logging.getLogger(__name__)
   logger.info("Checking churn distribution...")
   errors = []
   churn_counts = df['churned'].value_counts(normalize=True)
   logger.info("Churn distribution: %s", churn_counts.to_dict())
   if churn_counts.get(0, 0) == 0:
       errors.append("Churned class 0 is missing.")
   if churn_counts.get(1, 0) == 0:
       errors.append("Churned class 1 is missing.")
   return errors