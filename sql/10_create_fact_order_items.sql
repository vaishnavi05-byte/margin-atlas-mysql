USE margin_atlas;

CREATE TABLE fact_order_items (
    line_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    product_id INT UNSIGNED NOT NULL,
    quantity SMALLINT UNSIGNED NOT NULL,
    gross_paise BIGINT NOT NULL,
    discount_paise BIGINT NOT NULL,
    cogs_paise BIGINT NOT NULL,

    CONSTRAINT fk_items_order
        FOREIGN KEY (order_id)
        REFERENCES fact_orders(order_id),

    CONSTRAINT fk_items_product
        FOREIGN KEY (product_id)
        REFERENCES dim_product(product_id),

    CONSTRAINT chk_items_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_items_amounts
        CHECK (
            gross_paise >= 0
            AND discount_paise >= 0
            AND discount_paise <= gross_paise
            AND cogs_paise >= 0
        )
) ENGINE = InnoDB;

DESCRIBE fact_order_items;