SELECT SUM(oi.price)/COUNT(DISTINCT o.customer_id) AS aov
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id;
