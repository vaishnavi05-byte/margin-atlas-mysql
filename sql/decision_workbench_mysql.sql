-- Original extension of the user's margin_atlas schema. MySQL 8+.
-- Run after 00_rebuild_mysql.sql in the isolated decision_studio database.
-- Run SELECTs individually; CREATE VIEW requires the appropriate DB privilege.
USE decision_studio;

CREATE OR REPLACE SQL SECURITY INVOKER VIEW vw_decision_order_evidence AS
SELECT e.*, c.region, k.category,
       CONCAT(e.category_id, '|', COALESCE(NULLIF(c.region, ''), 'Unknown')) AS segment_key,
       CASE WHEN e.contribution_before_marketing_paise < 0 THEN 1 ELSE 0 END AS negative_order,
       GREATEST(-e.contribution_before_marketing_paise, 0) AS negative_contribution_paise,
       e.return_mature * e.return_flag AS mature_returns,
       CASE WHEN e.return_mature = 1 AND e.return_flag = 1
            THEN GREATEST(e.refund_paise-e.recovered_inventory_paise+e.reverse_logistics_paise,0)
            ELSE 0 END AS scenario_return_base_paise
FROM vw_order_economics e
JOIN dim_customer c ON c.customer_id=e.customer_id
JOIN dim_category k ON k.category_id=e.category_id;

-- Mutually exclusive category-region partitions: do not sum overlapping views.
WITH segments AS (
    SELECT segment_key, category, region, COUNT(*) AS orders,
           SUM(return_mature) AS mature_orders,
           SUM(mature_returns) AS mature_returns,
           SUM(negative_order) AS negative_orders,
           SUM(negative_contribution_paise) AS loss_exposure_paise,
           SUM(contribution_before_marketing_paise) AS net_segment_contribution_paise,
           SUM(scenario_return_base_paise) AS scenario_return_base_paise
    FROM vw_decision_order_evidence
    GROUP BY segment_key, category, region
), eligible AS (
    SELECT *, DENSE_RANK() OVER (ORDER BY loss_exposure_paise DESC) AS exposure_rank
    FROM segments WHERE mature_orders >= 100
)
SELECT *, mature_returns / NULLIF(mature_orders,0) AS mature_return_rate,
       -- Example only: avoid 15% of observed mature return costs, cost INR 10
       -- on every mature order. This is fixed-demand sensitivity, not uplift.
       (scenario_return_base_paise*0.15-mature_orders*1000)/100.0 AS scenario_net_change_inr
FROM eligible ORDER BY exposure_rank, segment_key;

-- Partition reconciliation: the two counts and paise totals must agree.
SELECT COUNT(*) AS orders,
       SUM(negative_contribution_paise) AS negative_contribution_paise,
       SUM(net_sales_paise) AS net_sales_paise
FROM vw_decision_order_evidence;

-- Preserve spend on dates/channels with no orders. No region/category allocation.
WITH commerce AS (
    SELECT order_date, channel_id,
           SUM(contribution_before_marketing_paise) AS contribution_paise
    FROM vw_order_economics GROUP BY order_date, channel_id
)
SELECT m.`date`, m.channel_id, COALESCE(c.contribution_paise,0) AS contribution_paise,
       m.spend_paise, COALESCE(c.contribution_paise,0)-m.spend_paise AS after_marketing_paise
FROM fact_marketing m
LEFT JOIN commerce c ON c.order_date=m.`date` AND c.channel_id=m.channel_id;
