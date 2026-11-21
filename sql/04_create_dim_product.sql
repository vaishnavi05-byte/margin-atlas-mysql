USE margin_atlas;

CREATE TABLE dim_product (
    product_id INT UNSIGNED PRIMARY KEY,
    category_id TINYINT UNSIGNED NOT NULL,
    product VARCHAR(100) NOT NULL,
    list_price_paise INT UNSIGNED NOT NULL,
    unit_cost_paise INT UNSIGNED NOT NULL,

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES dim_category(category_id),

    CONSTRAINT chk_product_price
        CHECK (list_price_paise > 0),

    CONSTRAINT chk_product_cost
        CHECK (unit_cost_paise > 0)
) ENGINE = InnoDB;

DESCRIBE dim_product;

