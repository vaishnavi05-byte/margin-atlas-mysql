USE margin_atlas;

CREATE TABLE dim_customer (
    customer_id INT UNSIGNED PRIMARY KEY,
    region VARCHAR(20) NOT NULL,
    city_tier VARCHAR(10) NOT NULL,
    acquisition_channel_id TINYINT UNSIGNED NOT NULL,
    first_order_date DATE NULL,

    CONSTRAINT fk_customer_channel
        FOREIGN KEY (acquisition_channel_id)
        REFERENCES dim_channel(channel_id)
) ENGINE = InnoDB;

DESCRIBE dim_customer;