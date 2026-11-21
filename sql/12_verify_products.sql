USE margin_atlas;

-- Show products with their category names and prices in rupees.
SELECT
    p.product_id,
    p.product,
    c.category,
    ROUND(p.list_price_paise / 100.0, 2) AS list_price_inr,
    ROUND(p.unit_cost_paise / 100.0, 2) AS unit_cost_inr
FROM dim_product AS p
JOIN dim_category AS c
    ON p.category_id = c.category_id
ORDER BY p.product_id
LIMIT 10;


-- Verify the number of products in each category.
SELECT
    c.category,
    COUNT(p.product_id) AS product_count
FROM dim_product AS p
JOIN dim_category AS c
    ON p.category_id = c.category_id
GROUP BY
    c.category_id,
    c.category
ORDER BY c.category_id;
