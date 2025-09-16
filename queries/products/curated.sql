/* ============================================================
   PRODUCT & SELLER FEATURES  (exact 10 columns)
   ============================================================ */
WITH product_agg AS (
    SELECT
        p.product_id,
        t.product_category_name_english AS category,
        AVG(oi.price)               AS avg_price,
        AVG(oi.freight_value)       AS avg_freight,
        COUNT(DISTINCT oi.order_id) AS orders_per_product,
        AVG(pr.review_score)        AS avg_review_score
    FROM products p
    LEFT JOIN order_items oi
           ON p.product_id = oi.product_id
    LEFT JOIN order_reviews pr
           ON oi.order_id = pr.order_id
    LEFT JOIN product_category_name_translation t
           ON p.product_category_name = t.product_category_name
    GROUP BY p.product_id, t.product_category_name_english
),
seller_agg AS (
    SELECT
        s.seller_id,
        COUNT(DISTINCT oi.order_id) AS orders_fulfilled,
        AVG(
            EXTRACT(EPOCH FROM (
                o.order_delivered_customer_date -
                o.order_delivered_carrier_date
            )) / 86400
        ) AS avg_ship_days,
        AVG(pr.review_score) AS avg_seller_review
    FROM sellers s
    LEFT JOIN order_items oi
           ON s.seller_id = oi.seller_id
    LEFT JOIN orders o
           ON oi.order_id = o.order_id
    LEFT JOIN order_reviews pr
           ON oi.order_id = pr.order_id
    GROUP BY s.seller_id
)
SELECT
    p.product_id,
    p.category,
    p.avg_price,
    p.avg_freight,
    p.orders_per_product,
    p.avg_review_score,
    s.seller_id,
    s.orders_fulfilled,
    s.avg_ship_days,
    s.avg_seller_review
FROM product_agg p
LEFT JOIN order_items oi
       ON p.product_id = oi.product_id
LEFT JOIN seller_agg s
       ON oi.seller_id = s.seller_id;
