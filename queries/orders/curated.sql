/* ============================================================
   ORDER-LEVEL FEATURES + OUTLIER FLAGS
   ============================================================ */
SELECT
    o.order_id,
    o.customer_id,

    -- Timing
    EXTRACT(EPOCH FROM (o.order_approved_at - o.order_purchase_timestamp))/3600
        AS hours_to_approval,
    EXTRACT(EPOCH FROM (o.order_delivered_carrier_date - o.order_approved_at))/86400
        AS days_to_carrier,
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_delivered_carrier_date))/86400
        AS days_carrier_to_customer,
    EXTRACT(EPOCH FROM (o.order_estimated_delivery_date - o.order_delivered_customer_date))/86400
        AS days_est_vs_actual,

    -- Monetary
    SUM(oi.price)  AS order_items_value,
    SUM(oi.freight_value) AS freight_value,
    SUM(oi.freight_value) / NULLIF(SUM(oi.price),0) AS freight_ratio,

    -- Basket composition
    COUNT(DISTINCT oi.seller_id) AS distinct_sellers,
    COUNT(DISTINCT oi.product_id) AS distinct_products,
    COUNT(*) AS total_items,

    -- Payment
    MAX(p.payment_installments) AS max_installments,
    MODE() WITHIN GROUP (ORDER BY p.payment_type) AS primary_payment_type,

    -- ----------------------------
    -- Outlier Flags
    -- ----------------------------
    CASE
        WHEN SUM(oi.freight_value) / NULLIF(SUM(oi.price),0) > 2
             OR SUM(oi.freight_value) / NULLIF(SUM(oi.price),0) < 0
        THEN 1 ELSE 0
    END AS freight_ratio_outlier,

    CASE WHEN
         EXTRACT(EPOCH FROM (o.order_delivered_carrier_date - o.order_approved_at))/86400 < 0
    THEN 1 ELSE 0 END AS neg_days_to_carrier,

    CASE WHEN
         EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_delivered_carrier_date))/86400 < 0
    THEN 1 ELSE 0 END AS neg_days_carrier_to_customer

FROM orders o
LEFT JOIN order_items     oi ON o.order_id = oi.order_id
LEFT JOIN order_payments  p  ON o.order_id = p.order_id
GROUP BY o.order_id, o.customer_id;
