SELECT DISTINCT o.customer_id, COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY o.customer_id
ORDER BY order_count ASC;
