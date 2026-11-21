USE margin_atlas;

ALTER TABLE fact_orders
    ADD COLUMN return_flag TINYINT UNSIGNED NOT NULL,
    ADD COLUMN late_flag TINYINT UNSIGNED NOT NULL,
    ADD COLUMN delivery_eligible TINYINT UNSIGNED NOT NULL,
    ADD COLUMN return_mature TINYINT UNSIGNED NOT NULL,
    ADD COLUMN new_customer TINYINT UNSIGNED NOT NULL,

    ADD CONSTRAINT chk_orders_binary_flags
        CHECK (
            return_flag IN (0, 1)
            AND late_flag IN (0, 1)
            AND delivery_eligible IN (0, 1)
            AND return_mature IN (0, 1)
            AND new_customer IN (0, 1)
        ),

    ADD CONSTRAINT chk_orders_eligible_flags
        CHECK (
            return_flag <= delivery_eligible
            AND late_flag <= delivery_eligible
            AND return_mature <= delivery_eligible
            AND new_customer <= delivery_eligible
        ),

    ADD CONSTRAINT chk_orders_refund_requires_return
        CHECK (
            refund_paise = 0 OR return_flag = 1
        );

SELECT COUNT(*) AS total_columns
FROM information_schema.columns
WHERE table_schema = DATABASE()
  AND table_name = 'fact_orders';