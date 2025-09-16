SELECT c.customer_state AS state, COUNT(DISTINCT c.customer_id) AS num_customers
FROM customers c
GROUP BY c.customer_state
ORDER BY num_customers DESC
