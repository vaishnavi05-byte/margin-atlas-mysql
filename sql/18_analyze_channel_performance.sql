USE margin_atlas;

-- 1. Financial performance by acquisition channel.
SELECT
    c.channel,

    ROUND(
        SUM(e.net_sales_paise) / 100.0, 2
    ) AS net_sales_inr,

    ROUND(
        SUM(e.marketing_spend_paise) / 100.0, 2
    ) AS marketing_spend_inr,

    ROUND(
        SUM(e.contribution_after_marketing_paise) / 100.0, 2
    ) AS contribution_after_marketing_inr,

    ROUND(
        100.0 * SUM(e.contribution_after_marketing_paise)
        / NULLIF(SUM(e.net_sales_paise), 0),
        2
    ) AS contribution_margin_pct

FROM vw_daily_channel_economics AS e
JOIN dim_channel AS c
    ON e.channel_id = c.channel_id

GROUP BY c.channel_id, c.channel
ORDER BY contribution_after_marketing_inr DESC;


-- 2. Recorded marketing spend per new purchasing customer.
SELECT
    c.channel,

    SUM(e.new_customers) AS new_purchasing_customers,

    ROUND(
        SUM(e.marketing_spend_paise)
        / NULLIF(SUM(e.new_customers), 0)
        / 100.0,
        2
    ) AS spend_per_new_customer_inr

FROM vw_daily_channel_economics AS e
JOIN dim_channel AS c
    ON e.channel_id = c.channel_id

GROUP BY c.channel_id, c.channel
ORDER BY spend_per_new_customer_inr DESC;