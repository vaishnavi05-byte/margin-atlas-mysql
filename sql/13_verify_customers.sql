USE margin_atlas;

-- 1. Count customer profiles by acquisition source.
SELECT
    ch.channel,
    COUNT(c.customer_id) AS customer_count
FROM dim_channel AS ch
LEFT JOIN dim_customer AS c
    ON ch.channel_id = c.acquisition_channel_id
GROUP BY
    ch.channel_id,
    ch.channel
ORDER BY ch.channel_id;


-- 2. Inspect the regional distribution.
SELECT
    region,
    COUNT(*) AS customer_count
FROM dim_customer
GROUP BY region
ORDER BY customer_count DESC, region;


-- 3. Check the loaded totals and repaired regions.
SELECT
    COUNT(*) AS total_customers,
    COUNT(DISTINCT customer_id) AS unique_customer_ids,
    SUM(region = 'Unknown') AS unknown_regions,
    SUM(first_order_date IS NULL) AS pending_first_order_dates
FROM dim_customer;