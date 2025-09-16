import logging
logger = logging.getLogger(__name__)
def compute_reference_values(engine):
    from sqlalchemy import text
    REFERENCE_VALUES = {}
    with engine.connect() as conn:
        REFERENCE_VALUES["total_revenue"] = float(conn.execute(
            text("SELECT SUM(price) FROM order_items")
        ).scalar())


        REFERENCE_VALUES["total_customers"] = float(conn.execute(
            text("SELECT COUNT(DISTINCT customer_id) FROM customers")
        ).scalar())         

        REFERENCE_VALUES["total_orders"] = float(conn.execute(
            text("SELECT COUNT(*) FROM orders")
        ).scalar()) 

        REFERENCE_VALUES["total_products"] = float(conn.execute(
            text("SELECT COUNT(*) FROM products")
        ).scalar())

        REFERENCE_VALUES["total_active_customers"] = float(conn.execute(
            text("""
                SELECT COUNT(DISTINCT o.customer_id) AS total_customers
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
            """)
        ).scalar())

        REFERENCE_VALUES["total_payments"] = float(conn.execute(
            text("""
                SELECT COUNT(*) FROM order_payments
            """)
        ).scalar())

        REFERENCE_VALUES["total_inactive_customers"] = float(conn.execute(
            text("""
                SELECT COUNT(DISTINCT c.customer_id) AS total_customers
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                WHERE o.order_id IS NULL OR oi.order_item_id IS NULL
            """)
        ).scalar())

        REFERENCE_VALUES["total_states"] = float(conn.execute(
            text("SELECT COUNT(DISTINCT customer_state) FROM customers")
        ).scalar())

        REFERENCE_VALUES["total_categories"] = float(conn.execute(
            text("SELECT COUNT(DISTINCT product_category_name) FROM products")
        ).scalar())

    return REFERENCE_VALUES


def not_empty(df):
    logger.info("Checking if DataFrame is not empty...")
    return not df.empty


# --- Common expectations ---
def total_revenue(df, rf):
    logger.info("Checking total revenue...")
    return abs(df["total_revenue"].sum() - rf["total_revenue"]) < 1e-6

def total_customers(df, rf):
    logger.info("Checking total customers...")
    return df["num_customers"].sum() == rf["total_customers"]

def active_customers(df, rf):
    logger.info("Checking active customers...")
    return df["num_customers"].sum() == rf["active_customers"]

def inactive_customers(df, rf):
    logger.info("Checking inactive customers...")
    return df["num_customers"].sum() == rf["inactive_customers"]

def total_products(df, rf):
    logger.info("Checking total products...")
    return df["num_products"].sum() == rf["total_products"]

def total_orders(df, rf):
    logger.info("Checking total orders...")
    return df["orders"].sum() == rf["total_orders"]

def total_catagories(df, rf):   
    logger.info("Checking total catagories...")
    return df["catagory"].count() == rf["total_catagories"]



# --- Customers ---

def customers_all(df, ref):
    logger.info("Checking customers all...")
    errors=[]
    """Validate customers_all query output."""
    df_n_customers = len(df)
    ref_n_customers = ref["total_customers"]
    if df_n_customers != ref_n_customers:
        errors.append(f"Number of customers in df {df_n_customers} does not match reference value {ref_n_customers}.")

    return errors


def customers_per_state(df, ref):
    logger.info("Checking customers per state...")
    """Validate customers_per_state query output."""
    errors = []
    df_n_states = df["state"].nunique()
    ref_n_states = ref["total_states"]
    if df_n_states != ref_n_states:
        errors.append(f"Number of states in df {df_n_states} does not match reference value {ref_n_states}.")
    #check number of customers
    df_n_customers = df["num_customers"].sum()
    ref_n_customers = ref["total_customers"]
    if df_n_customers != ref_n_customers:
        errors.append(f"Number of customers in df {df_n_customers} does not match reference value {ref_n_customers}.")
    return errors


def customers_who_orders_per_state(df, ref):
    logger.info("Checking customers who orders per state...")
    """Validate customers_who_orders_per_state query output."""
    errors = []
    df_n_states = df["state"].nunique()
    ref_n_states = ref["total_states"]
    if df_n_states != ref_n_states:
        errors.append(f"Number of states in df {df_n_states} does not match reference value {ref_n_states}.")
    #check number of customers
    df_n_customers = df["total_customers"].sum()
    ref_n_customers = ref["total_active_customers"]
    if df_n_customers != ref_n_customers:
        errors.append(f"Number of customers in df {df_n_customers} does not match reference value {ref_n_customers}.")
    return errors


def customers_no_orders(df, ref):
    logger.info("Checking customers with no orders...")
    """Validate customers_no_orders query output."""
    errors = []
    df_n_customers = len(df)
    ref_n_customers = ref["total_inactive_customers"]
    if df_n_customers != ref_n_customers:
        errors.append(f"Number of customers in df {df_n_customers} does not match reference value {ref_n_customers}.")
    return errors
    


def customers_orders_with_items(df, ref):
    logger.info("Checking customers orders with items...")
    """Validate customers_orders_with_items query output."""
    errors = []
    df_n_customers = len(df)
    ref_n_customers = ref["total_active_customers"]
    if df_n_customers != ref_n_customers:
        errors.append(f"Number of customers in df {df_n_customers} does not match reference value {ref_n_customers}.")
    return errors


# --- Products ---

def products_all(df, ref):
    logger.info("Checking all products...")
    """Validate products_all query output."""
    errors = []
    df_n_products = len(df)
    ref_n_products = ref["total_products"]
    if df_n_products != ref_n_products:
        errors.append(f"Number of products in df {df_n_products} does not match reference value {ref_n_products}.")
    return errors


def products_orders_per(df, ref):
    logger.info("Checking products orders per...")
    """Validate products_orders_per query output."""
    errors = []
    df_n_products = len(df)
    ref_n_products = ref["total_products"]
    if df_n_products != ref_n_products:
        errors.append(f"Number of products in df {df_n_products} does not match reference value {ref_n_products}.")
    return errors

def products_top_categories(df, ref):
    logger.info("Checking products top categories...")
    """Validate products_top_categories query output."""
    errors = []
    df_n_categories = len(df)
    ref_n_categories = ref["total_categories"]
    if df_n_categories != 1 + ref_n_categories:  # +1 for 'Unknown' category
        errors.append(f"Number of categories in df {df_n_categories} does not match reference value {ref_n_categories}.")
    df_total_sales = round(df["total_sales"].sum(), 2)
    ref_total_revenue = round(ref["total_revenue"], 2)
    if df_total_sales - ref_total_revenue > 1e-6:
        errors.append(f"Total sales in df {df_total_sales} does not match reference value {ref_total_revenue}.")
    return errors


# --- Revenue ---

def revenue_by_customer(df, ref):
    logger.info("Checking revenue by customer...")
    """Validate revenue_by_customer query output."""
    errors = []
    df_total_revenue = round(df["total_revenue"].sum(), 2)
    ref_total_revenue = round(ref["total_revenue"], 2)
    if df_total_revenue - ref_total_revenue > 1e-6:
        errors.append(f"Total revenue in df {df_total_revenue} does not match reference value {ref_total_revenue}.")
    return errors


def revenue_total(df, ref):
    logger.info("Checking total revenue...")
    """Validate revenue_total query output."""
    errors = []
    df_total_revenue = round(df["total_revenue"].sum(), 2)
    ref_total_revenue = round(ref["total_revenue"], 2)
    if df_total_revenue - ref_total_revenue > 1e-6:
        errors.append(f"Total revenue in df {df_total_revenue} does not match reference value {ref_total_revenue}.")
    return errors
    return not df.empty


def revenue_by_state(df, ref):
    logger.info("Checking revenue by state...")
    """Validate revenue_by_state query output."""
    errors = []
    df_total_revenue = round(df["total_revenue"].sum(), 2)
    ref_total_revenue = round(ref["total_revenue"], 2)
    if df_total_revenue - ref_total_revenue > 1e-6:
        errors.append(f"Total revenue in df {df_total_revenue} does not match reference value {ref_total_revenue}.")
    df_n_states = df["state"].nunique()
    ref_n_states = ref["total_states"]
    if df_n_states != ref_n_states:
        errors.append(f"Number of states in df {df_n_states} does not match reference value {ref_n_states}.")
    return errors

def customers_aov(df, ref):
    logger.info("Checking customers AOV...")
    """Validate customers_aov query output."""
    errors = []
    df_aov = round(df["aov"].sum(), 2)
    ref_total_revenue = round(ref["total_revenue"], 2)
    ref_total_customers = round(ref["total_active_customers"], 2)
    ref_aov = round(ref_total_revenue / ref_total_customers, 2) if ref_total_customers > 0 else 0
    if abs(df_aov - ref_aov) > 1e-6:
        errors.append(f"AOV in df {df_aov} does not match reference value {ref_aov}.")
    return errors

def customers_order_frequency(df, ref):
    logger.info("Checking customers order frequency...")
    """Validate customers_order_frequency query output."""
    errors = []
    df_total_orders = df["order_count"].sum()
    ref_total_orders = ref["total_orders"]
    if df_total_orders != ref_total_orders:
        errors.append(f"Total orders in df {df_total_orders} does not match reference value {ref_total_orders}.")
    df_n_customers = len(df)
    ref_n_customers = ref["total_customers"]
    if df_n_customers != ref_n_customers:
        errors.append(f"Number of customers in df {df_n_customers} does not match reference value {ref_n_customers}.")
    return errors

def customers_geo_location(df, ref):
    logger.info("Checking customers geo location...")
    """Validate customers_geo_location query output."""
    errors = []
    df_n_customers = len(df)
    ref_n_customers = ref["total_customers"]
    if df_n_customers != ref_n_customers:
        errors.append(f"Number of customers in df {df_n_customers} does not match reference value {ref_n_customers}.")
    return errors
def orders_all(df, ref):
    logger.info("Checking all orders...")
    """Validate orders_all query output."""
    errors = []
    df_n_orders = len(df)
    ref_n_orders = ref["total_orders"]
    if df_n_orders != ref_n_orders:
        errors.append(f"Number of orders in df {df_n_orders} does not match reference value {ref_n_orders}.")
    return errors

def orders_per_month(df, ref):
    logger.info("Checking orders per month...")
    """Validate orders_per_month query output."""
    errors = []
    df_total_orders = df["num_orders"].sum()
    ref_total_orders = ref["total_orders"]
    if df_total_orders != ref_total_orders:
        errors.append(f"Total orders in df {df_total_orders} does not match reference value {ref_total_orders}.")
    return errors

def payments_distribution(df, ref):
    logger.info("Checking payments distribution...")
    """Validate payments_distribution query output."""
    errors = []
    df_total_payments = df["num_payments"].sum()
    ref_total_orders = ref["total_payments"]
    if df_total_payments != ref_total_orders:
        errors.append(f"Total payments in df {df_total_payments} does not match reference value {ref_total_orders}.")
    return errors

def geo_location(df, ref):
    logger.info("Checking geo location...")
    """Validate geo_location query output."""
    errors = []
    df_n_orders = len(df)
    ref_n_orders = ref["total_orders"]
    if df_n_orders != ref_n_orders:
        errors.append(f"Number of orders in df {df_n_orders} does not match reference value {ref_n_orders}.")
    return errors
