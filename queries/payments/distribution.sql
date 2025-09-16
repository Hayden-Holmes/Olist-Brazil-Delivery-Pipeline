SELECT payment_type, COUNT(*) AS num_payments
FROM order_payments
GROUP BY payment_type
ORDER BY num_payments DESC;
