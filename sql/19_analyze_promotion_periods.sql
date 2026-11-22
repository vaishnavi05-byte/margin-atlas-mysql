USE margin_atlas;

SELECT
    c.channel,

    CASE
        WHEN o.order_date < '2026-03-01'
            THEN 'Before March 2026'
        ELSE 'March 2026 onward'
    END AS promotion_period,

    COUNT(*) AS mature_delivered_orders,

    ROUND(
        100.0 * SUM(o.discount_paise)
        / NULLIF(SUM(o.gross_paise), 0),
        2
    ) AS discount_pct,

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

JOIN dim_channel AS c
    ON o.channel_id = c.channel_id

WHERE o.delivery_eligible = 1
  AND o.return_mature = 1

GROUP BY
    c.channel_id,
    c.channel,
    promotion_period

ORDER BY
    c.channel_id,
    MIN(o.order_date);