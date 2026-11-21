USE margin_atlas;

CREATE TABLE dim_category (
    category_id TINYINT UNSIGNED PRIMARY KEY,
    category VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO dim_category (category_id, category)
VALUES
    (1, 'Apparel'),
    (2, 'Beauty'),
    (3, 'Home'),
    (4, 'Electronics'),
    (5, 'Wellness');

SELECT *
FROM dim_category
ORDER BY category_id;