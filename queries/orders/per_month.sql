SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS month, COUNT(o.order_id) AS num_orders
FROM orders o
GROUP BY month
ORDER BY month ASC;
