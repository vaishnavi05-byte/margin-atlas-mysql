USE margin_atlas;

CREATE TABLE fact_orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id INT UNSIGNED NOT NULL,
    order_date DATE NOT NULL,
    category_id TINYINT UNSIGNED NOT NULL,
    channel_id TINYINT UNSIGNED NOT NULL,
    payment_method VARCHAR(10) NOT NULL,
    promised_date DATE NOT NULL,
    delivered_date DATE NULL,
    status VARCHAR(15) NOT NULL,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customer(customer_id),

    CONSTRAINT fk_orders_date
        FOREIGN KEY (order_date)
        REFERENCES dim_date(`date`),

    CONSTRAINT fk_orders_category
        FOREIGN KEY (category_id)
        REFERENCES dim_category(category_id),

    CONSTRAINT fk_orders_channel
        FOREIGN KEY (channel_id)
        REFERENCES dim_channel(channel_id),

    CONSTRAINT chk_orders_payment
        CHECK (payment_method IN ('Prepaid', 'COD')),

    CONSTRAINT chk_orders_status
        CHECK (
            status IN ('Delivered', 'In transit', 'Cancelled')
        ),

    CONSTRAINT chk_orders_promised_date
        CHECK (promised_date >= order_date),

    CONSTRAINT chk_orders_delivered_date
        CHECK (delivered_date >= order_date)
) ENGINE = InnoDB;

DESCRIBE fact_orders;