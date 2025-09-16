SELECT
    c.customer_id,
    c.customer_zip_code_prefix,
    COALESCE(g.avg_lat, 0) AS avg_lat,
    COALESCE(g.avg_lng, 0) AS avg_lng
FROM customers c
LEFT JOIN (
    SELECT
        geolocation_zip_code_prefix,
        AVG(geolocation_lat) AS avg_lat,
        AVG(geolocation_lng) AS avg_lng
    FROM geolocation_filtered
    GROUP BY geolocation_zip_code_prefix
) g
ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix;
