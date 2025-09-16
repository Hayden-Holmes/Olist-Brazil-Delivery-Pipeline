import logging
import expectations as EX
import features_expectations as FE
import customer_features as CF
import product_features as PF
import order_features as OF

QUERY_TESTS = {
    # --- Customers ---
    "customers_all": [EX.customers_all],
    "customers_per_state": [EX.customers_per_state],
    "customers_who_orders_per_state": [EX.customers_who_orders_per_state],
    "customers_no_orders": [EX.customers_no_orders], 
    "customers_orders_with_items": [EX.customers_orders_with_items],
    "customers_aov": [EX.customers_aov],
    "customers_order_frequency": [EX.customers_order_frequency],
    "customers_geo_location": [EX.customers_geo_location],
    "customers_curated": [CF.run_all_expectations],

    # --- Products ---
    "products_all": [EX.products_all],
    "products_orders_per": [EX.products_orders_per],
    "products_top_categories": [EX.products_top_categories],
    "products_curated": [PF.run_all_expectations],

    # --- Revenue ---
    "revenue_by_customer": [EX.revenue_by_customer],
    "revenue_total": [EX.revenue_total],
    # "revenue_per_capita_per_state": [EX.revenue_per_capita_per_state],
    "revenue_by_state": [EX.revenue_by_state],


    # --- Orders ---
    "orders_all": [EX.orders_all],
    "orders_per_month": [EX.orders_per_month],
    "geo_location": [EX.geo_location],
    "orders_curated": [OF.run_all_expectations],

    # --- Payments ---
    "payments_distribution": [EX.payments_distribution],

    # --- Features ---
    "ML_churn_features": [
        FE.total_spent_non_negative, FE.total_spent_consistent,
        FE.avg_order_value_valid, FE.recency_non_negative, FE.frequency_non_negative, FE.distinct_products_non_negative, FE.state_dummies_valid, FE.churned_binary_valid, FE.churned_consistent, FE.check_non_null
    ],
}


def get(name: str):
    """Return the list of expectations for a given query name."""
    logging.info(f"Retrieving tests for query: {name}, tests found: {QUERY_TESTS.get(name, [])}")
    return QUERY_TESTS.get(name, [])
