USE margin_atlas;

CREATE TABLE dim_date (
    `date` DATE PRIMARY KEY,
    `month` CHAR(7) NOT NULL,
    `year` SMALLINT UNSIGNED NOT NULL,
    month_number TINYINT UNSIGNED NOT NULL,

    CONSTRAINT chk_month_number
        CHECK (month_number BETWEEN 1 AND 12)
) ENGINE = InnoDB;


INSERT INTO dim_date (
    `date`,
    `month`,
    `year`,
    month_number
)
WITH RECURSIVE calendar AS (
    SELECT CAST('2025-01-01' AS DATE) AS calendar_date

    UNION ALL

    SELECT DATE_ADD(calendar_date, INTERVAL 1 DAY)
    FROM calendar
    WHERE calendar_date < '2026-09-30'
)
SELECT
    calendar_date,
    DATE_FORMAT(calendar_date, '%Y-%m'),
    YEAR(calendar_date),
    MONTH(calendar_date)
FROM calendar;


SELECT
    COUNT(*) AS total_dates,
    MIN(`date`) AS first_date,
    MAX(`date`) AS last_date
FROM dim_date;