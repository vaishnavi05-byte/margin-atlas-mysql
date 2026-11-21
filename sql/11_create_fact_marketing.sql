USE margin_atlas;

CREATE TABLE fact_marketing (
    `date` DATE NOT NULL,
    channel_id TINYINT UNSIGNED NOT NULL,
    spend_paise BIGINT NOT NULL,

    PRIMARY KEY (`date`, channel_id),

    CONSTRAINT fk_marketing_date
        FOREIGN KEY (`date`)
        REFERENCES dim_date(`date`),

    CONSTRAINT fk_marketing_channel
        FOREIGN KEY (channel_id)
        REFERENCES dim_channel(channel_id),

    CONSTRAINT chk_marketing_spend
        CHECK (spend_paise >= 0)
) ENGINE = InnoDB;

DESCRIBE fact_marketing;