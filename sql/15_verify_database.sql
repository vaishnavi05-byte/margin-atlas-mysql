USE margin_atlas;

-- 1. Count rows in every project table.
SELECT 'dim_channel' AS table_name, COUNT(*) AS row_count
FROM dim_channel
UNION ALL
SELECT 'dim_category', COUNT(*) FROM dim_category
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_orders', COUNT(*) FROM fact_orders
UNION ALL
SELECT 'fact_order_items', COUNT(*) FROM fact_order_items
UNION ALL
SELECT 'fact_marketing', COUNT(*) FROM fact_marketing;

-- 2. Summarize the order indicators.
SELECT
    COUNT(*) AS total_orders,
    SUM(status = 'Delivered') AS delivered_orders,
    SUM(status = 'Cancelled') AS cancelled_orders,
    SUM(status = 'In transit') AS in_transit_orders,
    SUM(late_flag) AS late_delivered_orders,
    SUM(return_flag) AS observed_returns,
    SUM(return_mature) AS return_mature_orders,
    SUM(new_customer) AS customers_with_purchase
FROM fact_orders;

-- 3. All issue counts below should be zero.
WITH line_totals AS (
    SELECT
        order_id,
        SUM(gross_paise) AS gross_paise,
        SUM(discount_paise) AS discount_paise,
        SUM(cogs_paise) AS cogs_paise
    FROM fact_order_items
    GROUP BY order_id
),
first_purchases AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_purchase_date
    FROM fact_orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    'Order amounts differ from product lines' AS quality_check,
    COUNT(*) AS issue_count
FROM fact_orders AS o
LEFT JOIN line_totals AS i
    ON o.order_id = i.order_id
WHERE i.order_id IS NULL
   OR o.gross_paise <> i.gross_paise
   OR o.discount_paise <> i.discount_paise
   OR o.cogs_paise <> i.cogs_paise

UNION ALL

SELECT
    'Customer first-purchase dates differ',
    COUNT(*)
FROM dim_customer AS c
LEFT JOIN first_purchases AS p
    ON c.customer_id = p.customer_id
WHERE NOT (c.first_order_date <=> p.first_purchase_date)

UNION ALL

SELECT
    'Missing marketing date-channel pairs',
    COUNT(*)
FROM dim_date AS d
CROSS JOIN dim_channel AS c
LEFT JOIN fact_marketing AS m
    ON m.`date` = d.`date`
   AND m.channel_id = c.channel_id
WHERE m.`date` IS NULL;