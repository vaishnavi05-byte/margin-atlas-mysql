USE margin_atlas;

-- Temporarily adjust safe-update mode for this session.
SET @previous_safe_updates = @@SESSION.sql_safe_updates;
SET SESSION sql_safe_updates = 0;

UPDATE dim_customer AS c
LEFT JOIN (
    SELECT
        customer_id,
        MIN(order_date) AS first_purchase_date
    FROM fact_orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
) AS p
    ON c.customer_id = p.customer_id
SET c.first_order_date = p.first_purchase_date;

-- Restore the previous setting.
SET SESSION sql_safe_updates = @previous_safe_updates;

-- Check how many customers now have a first-purchase date.
SELECT
    COUNT(*) AS total_customers,
    SUM(first_order_date IS NOT NULL) AS customers_with_purchase,
    SUM(first_order_date IS NULL) AS customers_without_purchase
FROM dim_customer;

-- Verify every stored date against the delivered orders.
SELECT
    COUNT(*) AS first_purchase_date_mismatches
FROM dim_customer AS c
LEFT JOIN (
    SELECT
        customer_id,
        MIN(order_date) AS first_purchase_date
    FROM fact_orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
) AS p
    ON c.customer_id = p.customer_id
WHERE NOT (c.first_order_date <=> p.first_purchase_date);