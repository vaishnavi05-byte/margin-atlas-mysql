USE margin_atlas;

CREATE TABLE dim_channel (
    channel_id TINYINT UNSIGNED PRIMARY KEY,
    channel VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO dim_channel (channel_id, channel)
VALUES
    (1, 'Organic'),
    (2, 'Paid Search'),
    (3, 'Paid Social'),
    (4, 'Email'),
    (5, 'Affiliate');

SELECT *
FROM dim_channel
ORDER BY channel_id;