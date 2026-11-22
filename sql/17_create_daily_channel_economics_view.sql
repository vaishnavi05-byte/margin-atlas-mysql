USE margin_atlas;

CREATE OR REPLACE
SQL SECURITY INVOKER
VIEW vw_daily_channel_economics AS
SELECT
    m.`date`,
    m.channel_id,

    COALESCE(o.placed_orders, 0) AS placed_orders,
    COALESCE(o.delivered_orders, 0) AS delivered_orders,
    COALESCE(o.new_customers, 0) AS new_customers,

    COALESCE(o.net_sales_paise, 0) AS net_sales_paise,

    COALESCE(
        o.contribution_before_marketing_paise, 0
    ) AS contribution_before_marketing_paise,

    m.spend_paise AS marketing_spend_paise,

    (
        COALESCE(o.contribution_before_marketing_paise, 0)
        - m.spend_paise
    ) AS contribution_after_marketing_paise

FROM fact_marketing AS m

LEFT JOIN (
    SELECT
        order_date,
        channel_id,
        COUNT(*) AS placed_orders,
        SUM(delivery_eligible) AS delivered_orders,
        SUM(new_customer) AS new_customers,
        SUM(net_sales_paise) AS net_sales_paise,

        SUM(
            contribution_before_marketing_paise
        ) AS contribution_before_marketing_paise

    FROM vw_order_economics
    GROUP BY order_date, channel_id
) AS o
    ON m.`date` = o.order_date
   AND m.channel_id = o.channel_id;

-- Check the combined data's coverage.
SELECT
    COUNT(*) AS date_channel_rows,
    SUM(placed_orders) AS total_orders,
    SUM(new_customers) AS customers_with_purchase
FROM vw_daily_channel_economics;

-- Calculate contribution after marketing, in rupees.
SELECT
    ROUND(
        SUM(net_sales_paise) / 100.0, 2
    ) AS net_sales_inr,

    ROUND(
        SUM(marketing_spend_paise) / 100.0, 2
    ) AS marketing_spend_inr,

    ROUND(
        SUM(contribution_after_marketing_paise) / 100.0, 2
    ) AS contribution_after_marketing_inr

FROM vw_daily_channel_economics;