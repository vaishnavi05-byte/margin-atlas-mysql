USE decision_studio;

-- Monthly sales and change: calendar spine retains zero-order months.
WITH calendar AS (SELECT DISTINCT `month` FROM dim_date),
monthly AS (SELECT DATE_FORMAT(order_date,'%Y-%m') AS `month`,COUNT(*) AS orders,SUM(net_sales_paise) AS sales_paise FROM fact_orders GROUP BY 1),
complete AS (SELECT c.`month`,COALESCE(m.orders,0) AS orders,COALESCE(m.sales_paise,0) AS sales_paise FROM calendar c LEFT JOIN monthly m USING (`month`)),
lagged AS (SELECT *,LAG(sales_paise) OVER(ORDER BY `month`) AS previous_paise FROM complete)
SELECT `month`,orders,sales_paise/100.0 AS net_sales_inr,(sales_paise-previous_paise)/NULLIF(previous_paise,0) AS month_on_month_rate FROM lagged ORDER BY `month`;

-- Complete 90-day cohort windows; repeat orders must be placed AND delivered
-- before the customer's boundary. Cohort month ends must have full follow-up.
WITH delivered AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date,order_id) AS rn
 FROM fact_orders WHERE status='Delivered' AND delivered_date IS NOT NULL
), first_purchase AS (
 SELECT customer_id,order_id AS first_id,order_date AS first_date FROM delivered WHERE rn=1
), eligible AS (
 SELECT * FROM first_purchase WHERE DATE_ADD(LAST_DAY(first_date),INTERVAL 90 DAY)<='2026-09-30'
), customer_outcomes AS (
 SELECT f.customer_id,DATE_FORMAT(f.first_date,'%Y-%m') AS cohort,
 MAX(CASE WHEN d.order_id<>f.first_id AND d.order_date<DATE_ADD(f.first_date,INTERVAL 90 DAY)
 AND d.delivered_date<DATE_ADD(f.first_date,INTERVAL 90 DAY) THEN 1 ELSE 0 END) AS repeat_90d
 FROM eligible f JOIN delivered d ON d.customer_id=f.customer_id GROUP BY f.customer_id,f.first_date
)
SELECT cohort,COUNT(*) AS customers,SUM(repeat_90d) AS repeat_customers,SUM(repeat_90d)/COUNT(*) AS repeat_rate
FROM customer_outcomes GROUP BY cohort ORDER BY cohort;

-- Descriptive association, NOT a causal delivery effect.
SELECT late_flag,COUNT(*) AS mature_orders,SUM(return_flag) AS returns,
 SUM(return_flag)/COUNT(*) AS mature_return_rate
FROM fact_orders WHERE return_mature=1 GROUP BY late_flag;

-- Grain audit: every row should have zero mismatched orders.
WITH item_totals AS (
 SELECT order_id,SUM(gross_paise) AS gross_paise,SUM(discount_paise) AS discount_paise,SUM(cogs_paise) AS cogs_paise FROM fact_order_items GROUP BY order_id
)
SELECT SUM(l.order_id IS NULL OR o.gross_paise<>l.gross_paise OR o.discount_paise<>l.discount_paise OR o.cogs_paise<>l.cogs_paise) AS mismatched_orders
FROM fact_orders o LEFT JOIN item_totals l ON l.order_id=o.order_id;
