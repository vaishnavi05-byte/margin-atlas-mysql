USE margin_atlas;

CREATE OR REPLACE
SQL SECURITY INVOKER
VIEW vw_order_economics AS
SELECT
    o.*,

    (
        o.gross_paise
        - o.discount_paise
        - o.refund_paise
    ) AS net_sales_paise,

    (
        o.cogs_paise
        - o.recovered_inventory_paise
    ) AS net_product_cost_paise,

    (
        o.gross_paise
        - o.discount_paise
        - o.refund_paise
        - o.cogs_paise
        + o.recovered_inventory_paise
        - o.fulfilment_paise
        - o.payment_fee_paise
        - o.reverse_logistics_paise
    ) AS contribution_before_marketing_paise

FROM fact_orders AS o;

-- Summarize the order economics in rupees.
SELECT
    COUNT(*) AS total_orders,

    ROUND(
        SUM(net_sales_paise) / 100.0,
        2
    ) AS net_sales_inr,

    ROUND(
        SUM(contribution_before_marketing_paise) / 100.0,
        2
    ) AS contribution_before_marketing_inr

FROM vw_order_economics;