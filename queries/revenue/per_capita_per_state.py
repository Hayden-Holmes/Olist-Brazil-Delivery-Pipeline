import pandas as pd


def per_capita_per_state(total_revenue_per_state, total_customers_per_state):
    # Merge on state
    merged = pd.merge(
        total_revenue_per_state,
        total_customers_per_state,
        on="customer_state",
        how="inner"
    )

    # Compute revenue per capita
    merged["revenue_per_capita"] = (
        merged["total_revenue"] / merged["total_customers"]
    )

    # Reorder columns for readability
    merged = merged[["customer_state", "revenue_per_capita", "total_revenue", "total_customers"]]

    return merged

