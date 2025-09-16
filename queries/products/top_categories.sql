SELECT 
    COALESCE(c.product_category_name_english, p.product_category_name, 'Unknown') AS category,
    COALESCE(SUM(oi.price), 0) AS total_sales
FROM products p
LEFT JOIN product_category_name_translation c 
    ON p.product_category_name = c.product_category_name
LEFT JOIN order_items oi 
    ON p.product_id = oi.product_id
GROUP BY COALESCE(c.product_category_name_english, p.product_category_name, 'Unknown')
ORDER BY total_sales DESC;


