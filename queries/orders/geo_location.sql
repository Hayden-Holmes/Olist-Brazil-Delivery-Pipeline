SELECT
    o.order_id,
    o.customer_id,
    c.customer_zip_code_prefix,
    COALESCE(g.avg_lat, 0) AS order_lat,
    COALESCE(g.avg_lng, 0) AS order_lng
FROM orders o
JOIN customers c
       ON o.customer_id = c.customer_id        -- link each order to its customer
LEFT JOIN (
    SELECT
        geolocation_zip_code_prefix,
        AVG(geolocation_lat) AS avg_lat,
        AVG(geolocation_lng) AS avg_lng
    FROM geolocation_filtered
    GROUP BY geolocation_zip_code_prefix
) g
       ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix;
