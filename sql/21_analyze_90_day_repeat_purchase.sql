USE margin_atlas;

SET @snapshot_date = '2026-09-30';

WITH eligible_customers AS (
    SELECT
        customer_id,
        first_order_date

    FROM dim_customer

    WHERE first_order_date IS NOT NULL

      -- Require a complete observation window for the whole month.
      AND DATE_ADD(
          LAST_DAY(first_order_date),
          INTERVAL 90 DAY
      ) <= @snapshot_date
),

customer_repeat AS (
    SELECT
        c.customer_id,
        c.first_order_date,

        MAX(
            CASE
                WHEN o.new_customer = 0 THEN 1
                ELSE 0
            END
        ) AS repeated_within_90_days

    FROM eligible_customers AS c

    LEFT JOIN fact_orders AS o
        ON c.customer_id = o.customer_id
       AND o.status = 'Delivered'

       -- Purchase and delivery must fall within the window.
       AND o.order_date >= c.first_order_date
       AND o.order_date < DATE_ADD(
           c.first_order_date,
           INTERVAL 90 DAY
       )
       AND o.delivered_date < DATE_ADD(
           c.first_order_date,
           INTERVAL 90 DAY
       )

    GROUP BY
        c.customer_id,
        c.first_order_date
)

SELECT
    DATE_FORMAT(
        first_order_date, '%Y-%m'
    ) AS first_purchase_month,

    COUNT(*) AS cohort_customers,

    SUM(
        repeated_within_90_days
    ) AS repeat_customers_90d,

    ROUND(
        100.0 * SUM(repeated_within_90_days)
        / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_purchase_rate_90d_pct

FROM customer_repeat

GROUP BY DATE_FORMAT(first_order_date, '%Y-%m')
ORDER BY first_purchase_month;