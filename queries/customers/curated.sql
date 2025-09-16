/* Customer-level features in one query */
SELECT
    cl.customer_unique_id,

    -- basic lifetime metrics
    cl.total_orders,
    cl.first_purchase_ts,
    cl.last_purchase_ts,
    EXTRACT(EPOCH FROM (cl.last_purchase_ts - cl.first_purchase_ts))/86400
        AS tenure_days,

    -- monetary metrics
    m.avg_order_value,
    m.total_spent,

    -- basket metrics
    b.avg_items_per_order,

    -- repeat-purchase behaviour
    i.avg_days_between_orders,

    -- payment behaviour
    p.preferred_payment_type,
    p.avg_installments,

    -- geography (from latest order)
    g.customer_city,
    g.customer_state
FROM
(
    /* lifetime: total orders & first/last purchase */
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id)           AS total_orders,
        MIN(o.order_purchase_timestamp)      AS first_purchase_ts,
        MAX(o.order_purchase_timestamp)      AS last_purchase_ts
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
) AS cl
LEFT JOIN
(
    /* monetary: avg order value & total spend */
    SELECT
        c.customer_unique_id,
        SUM(p.payment_value)/COUNT(DISTINCT o.order_id) AS avg_order_value,
        SUM(p.payment_value) AS total_spent
    FROM customers c
    JOIN orders o      ON o.customer_id = c.customer_id
    JOIN order_payments p ON p.order_id = o.order_id
    GROUP BY c.customer_unique_id
) AS m
    ON cl.customer_unique_id = m.customer_unique_id
LEFT JOIN
(
    /* basket size: avg items per order */
    SELECT
        c.customer_unique_id,
        AVG(items_per_order) AS avg_items_per_order
    FROM (
        SELECT
            o.customer_id,
            o.order_id,
            COUNT(oi.order_item_id) AS items_per_order
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.customer_id, o.order_id
    ) t
    JOIN customers c ON c.customer_id = t.customer_id
    GROUP BY c.customer_unique_id
) AS b
    ON cl.customer_unique_id = b.customer_unique_id
LEFT JOIN
(
    /* inter-purchase interval */
    WITH ordered AS (
        SELECT
            c.customer_unique_id,
            o.order_purchase_timestamp,
            LAG(o.order_purchase_timestamp) OVER (
                PARTITION BY c.customer_unique_id
                ORDER BY o.order_purchase_timestamp
            ) AS prev_ts
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
    )
    SELECT
        customer_unique_id,
        AVG(EXTRACT(EPOCH FROM (order_purchase_timestamp - prev_ts))/86400)
            AS avg_days_between_orders
    FROM ordered
    WHERE prev_ts IS NOT NULL
    GROUP BY customer_unique_id
) AS i
    ON cl.customer_unique_id = i.customer_unique_id
LEFT JOIN
(
    /* payment behaviour: preferred type & avg installments */
    SELECT
        c.customer_unique_id,
        MODE() WITHIN GROUP (ORDER BY p.payment_type) AS preferred_payment_type,
        AVG(p.payment_installments)                   AS avg_installments
    FROM customers c
    JOIN orders o      ON o.customer_id = c.customer_id
    JOIN order_payments p ON p.order_id = o.order_id
    GROUP BY c.customer_unique_id
) AS p
    ON cl.customer_unique_id = p.customer_unique_id
LEFT JOIN
(
    /* latest geography */
    SELECT DISTINCT ON (c.customer_unique_id)
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        o.order_purchase_timestamp
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    ORDER BY c.customer_unique_id, o.order_purchase_timestamp DESC
) AS g
    ON cl.customer_unique_id = g.customer_unique_id;
