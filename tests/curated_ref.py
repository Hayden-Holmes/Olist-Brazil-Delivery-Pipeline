import pandas as pd
def compute_reference_values(engine):
    ref = {}

    # --- Core counts & totals ---
    ref["total_customers"] = pd.read_sql(
        "SELECT COUNT(DISTINCT customer_unique_id) AS n FROM customers", engine
    )["n"].iloc[0]

    ref["total_gross_revenue"] = pd.read_sql(
        "SELECT SUM(oi.price) AS s FROM order_items oi", engine
    )["s"].iloc[0]

    ref["total_orders"] = pd.read_sql(
        "SELECT COUNT(*) AS n FROM orders", engine
    )["n"].iloc[0]

    ref["total_revenue"] = pd.read_sql(
        "SELECT SUM(payment_value) AS s FROM order_payments", engine
    )["s"].iloc[0]

    ref["total_products"] = pd.read_sql(
        "SELECT COUNT(DISTINCT product_id) AS n FROM products", engine
    )["n"].iloc[0]

    ref["total_sellers"] = pd.read_sql(
        "SELECT COUNT(DISTINCT seller_id) AS n FROM sellers", engine
    )["n"].iloc[0]

    ref["total_order_items"] = pd.read_sql(
        "SELECT COUNT(*) AS n FROM order_items", engine
    )["n"].iloc[0]

    # Dataset time span for tenure bounds
    ref["dataset_span_days"] = pd.read_sql("""
        SELECT EXTRACT(EPOCH FROM (
            MAX(order_purchase_timestamp) - MIN(order_purchase_timestamp)
        ))/86400 AS span
        FROM orders
    """, engine)["span"].iloc[0]

    # Expected column lists for schema checks
    ref["expected_customer_cols"] = [
        "customer_unique_id","total_orders","first_purchase_ts","last_purchase_ts",
        "tenure_days","avg_order_value","total_spent","avg_items_per_order",
        "avg_days_between_orders","preferred_payment_type","avg_installments",
        "customer_city","customer_state"
    ]

    ref["expected_order_cols"] = [
        "order_id","customer_id","hours_to_approval","days_to_carrier",
        "days_carrier_to_customer","days_est_vs_actual","order_items_value",
        "freight_value","freight_ratio","distinct_sellers",
        "distinct_products","total_items","max_installments",
        "primary_payment_type"
    ]

    ref["expected_product_seller_cols"] = [
        "product_id","category","avg_price","avg_freight",
        "orders_per_product","avg_review_score",
        "seller_id","orders_fulfilled","avg_ship_days","avg_seller_review"
    ]

     

    # Optional percentile heuristics
    ref["max_orders_95pct"] = 50
    ref["max_spent_95pct"]  = 20000
    ref["max_ship_days_95pct"] = 60
    return ref
