SELECT p.product_id, COUNT(oi.order_id) AS num_orders
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id
ORDER BY num_orders DESC


