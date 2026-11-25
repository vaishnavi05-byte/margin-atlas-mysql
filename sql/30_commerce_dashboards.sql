USE decision_studio;

-- Date/channel spend remains at its own grain; no product allocation or CAC.
WITH commerce AS (
 SELECT channel_id,COUNT(*) AS placed_orders,SUM(net_sales_paise) AS net_sales_paise,
 SUM(contribution_before_marketing_paise) AS contribution_paise
 FROM fact_orders GROUP BY channel_id
), spend AS (SELECT channel_id,SUM(spend_paise) AS spend_paise FROM fact_marketing GROUP BY channel_id)
SELECT d.channel,COALESCE(c.placed_orders,0) AS placed_orders,
 COALESCE(c.net_sales_paise,0)/100.0 AS net_sales_inr,s.spend_paise/100.0 AS spend_inr,
 (COALESCE(c.contribution_paise,0)-s.spend_paise)/100.0 AS after_marketing_inr
FROM dim_channel d JOIN spend s USING(channel_id) LEFT JOIN commerce c USING(channel_id)
ORDER BY after_marketing_inr DESC;

-- Exact integer ratio boundaries. Zero recognized sales is not a zero-discount sale.
WITH bands AS (
 SELECT *,CASE WHEN gross_paise=0 THEN 'No recognized sales'
 WHEN discount_paise=0 THEN '0%'
 WHEN discount_paise*100<=gross_paise*10 THEN '1-10%'
 WHEN discount_paise*100<=gross_paise*20 THEN '11-20%'
 WHEN discount_paise*100<=gross_paise*30 THEN '21-30%' ELSE 'Above 30%' END AS discount_band
 FROM fact_orders
)
SELECT discount_band,COUNT(*) AS placed_orders,SUM(net_sales_paise)/100.0 AS net_sales_inr,
 SUM(contribution_before_marketing_paise)/100.0 AS contribution_inr,
 SUM(return_mature) AS mature_orders,SUM(return_flag*return_mature)/NULLIF(SUM(return_mature),0) AS mature_return_rate
FROM bands GROUP BY discount_band ORDER BY discount_band;

-- Shipped denominator includes in-transit orders; cancelled orders remain visible.
SELECT payment_method,status,COUNT(*) AS placed_orders,
 SUM(fulfilment_paise+payment_fee_paise+reverse_logistics_paise)/100.0 AS service_cost_inr,
 SUM(contribution_before_marketing_paise)/100.0 AS contribution_inr
FROM fact_orders GROUP BY payment_method,status ORDER BY payment_method,status;

-- Item grain is authoritative here. No allocation of refunds/shared order costs.
SELECT p.product_id,p.product,
 SUM(i.quantity*o.delivery_eligible) AS recognized_units,
 COUNT(DISTINCT CASE WHEN o.delivery_eligible=1 THEN i.order_id END) AS delivered_item_orders,
 SUM(i.gross_paise-i.discount_paise)/100.0 AS item_sales_before_refund_inr,
 SUM(i.gross_paise-i.discount_paise-i.cogs_paise)/100.0 AS item_merchandise_margin_inr
FROM fact_order_items i JOIN fact_orders o ON o.order_id=i.order_id
JOIN dim_product p ON p.product_id=i.product_id
GROUP BY p.product_id,p.product ORDER BY item_sales_before_refund_inr DESC;
