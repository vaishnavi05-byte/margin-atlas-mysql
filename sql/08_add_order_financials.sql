USE margin_atlas;

ALTER TABLE fact_orders
    ADD COLUMN gross_paise BIGINT NOT NULL,
    ADD COLUMN discount_paise BIGINT NOT NULL,
    ADD COLUMN refund_paise BIGINT NOT NULL,
    ADD COLUMN cogs_paise BIGINT NOT NULL,
    ADD COLUMN recovered_inventory_paise BIGINT NOT NULL,
    ADD COLUMN fulfilment_paise BIGINT NOT NULL,
    ADD COLUMN payment_fee_paise BIGINT NOT NULL,
    ADD COLUMN reverse_logistics_paise BIGINT NOT NULL,

    ADD CONSTRAINT chk_orders_nonnegative_amounts
        CHECK (
            gross_paise >= 0
            AND discount_paise >= 0
            AND refund_paise >= 0
            AND cogs_paise >= 0
            AND recovered_inventory_paise >= 0
            AND fulfilment_paise >= 0
            AND payment_fee_paise >= 0
            AND reverse_logistics_paise >= 0
        ),

    ADD CONSTRAINT chk_orders_discount
        CHECK (discount_paise <= gross_paise),

    ADD CONSTRAINT chk_orders_refund
        CHECK (
            refund_paise <= gross_paise - discount_paise
        ),

    ADD CONSTRAINT chk_orders_inventory_recovery
        CHECK (recovered_inventory_paise <= cogs_paise);

DESCRIBE fact_orders;