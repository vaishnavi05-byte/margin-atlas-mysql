USE margin_atlas;

SELECT
    c.region,

    CASE
        WHEN o.order_date < '2026-05-01'
            THEN 'Before May 2026'
        ELSE 'May 2026 onward'
    END AS delivery_period,

    COUNT(*) AS mature_delivered_orders,

    ROUND(
        100.0 * SUM(o.late_flag)
        / NULLIF(COUNT(*), 0),
        2
    ) AS late_delivery_pct,

    ROUND(
        100.0 * SUM(o.return_flag)
        / NULLIF(COUNT(*), 0),
        2
    ) AS return_rate_pct,

    ROUND(
        AVG(o.contribution_before_marketing_paise) / 100.0,
        2
    ) AS contribution_per_order_inr

FROM vw_order_economics AS o

JOIN dim_customer AS c
    ON o.customer_id = c.customer_id

WHERE o.delivery_eligible = 1
  AND o.return_mature = 1

GROUP BY
    c.region,
    delivery_period

ORDER BY
    c.region,
    MIN(o.order_date);