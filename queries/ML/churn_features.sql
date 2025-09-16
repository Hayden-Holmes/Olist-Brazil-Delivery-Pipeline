WITH customer_orders AS (
    SELECT 
        o.customer_id,
        COUNT(o.order_id) AS total_orders,
        SUM(oi.price) AS total_spent,
        AVG(oi.price) AS avg_order_value,
        MAX(o.order_purchase_timestamp) AS last_order_date,
        COUNT(DISTINCT oi.product_id) AS distinct_products,
        MIN(o.order_purchase_timestamp) AS first_order_date
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
),
customer_recency AS (
    SELECT 
        customer_id,
        total_orders,
        total_spent,
        avg_order_value,
        distinct_products,
        DATE_PART('day', CURRENT_DATE - last_order_date) AS recency,
        DATE_PART('month', CURRENT_DATE - first_order_date) AS customer_age
    FROM customer_orders
),
customer_frequency AS (
    SELECT 
        customer_id,
        total_orders,
        total_spent,
        avg_order_value,
        distinct_products,
        recency,
        CASE 
            WHEN customer_age > 0 THEN total_orders / customer_age
            ELSE total_orders
        END AS frequency
    FROM customer_recency
),
customer_state AS (
    SELECT 
        c.customer_id,
        c.customer_state
    FROM customers c
),
-- 🟢 Add categories purchased per customer
customer_categories AS (
    SELECT 
        o.customer_id,
        c.product_category_name_english,
        SUM(oi.price) AS category_spent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_name_translation c 
           ON p.product_category_name = c.product_category_name
    GROUP BY o.customer_id, c.product_category_name_english
),
-- 🟢 Rank categories globally by sales
top_categories AS (
    SELECT product_category_name_english
    FROM customer_categories
    GROUP BY product_category_name_english
    ORDER BY SUM(category_spent) DESC
    LIMIT 5
),
ch AS (
    WITH last_order AS (
        SELECT customer_id, MAX(order_purchase_timestamp) AS last_order_date
        FROM orders
        GROUP BY customer_id
    )
    SELECT 
        c.customer_id,
        CASE WHEN ((SELECT MAX(order_purchase_timestamp)::date FROM orders)- lo.last_order_date::date) > 90 THEN 1 ELSE 0 END AS churned
    FROM customers c
    LEFT JOIN last_order lo ON c.customer_id = lo.customer_id
)
SELECT 
    f.*,
    s.customer_state,
    ch.churned
FROM customer_frequency f
JOIN customer_state s ON f.customer_id = s.customer_id
JOIN ch ON f.customer_id = ch.customer_id
WHERE f.total_orders > 0;
-- Note: Customers without purchases will be excluded from this analysis.