SELECT DISTINCT c.customer_id
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_id IS NULL OR oi.order_item_id IS NULL
