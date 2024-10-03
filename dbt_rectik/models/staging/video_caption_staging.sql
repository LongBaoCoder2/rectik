WITH source_data AS (
    SELECT *
    FROM {{ source('postgres_database', 'video_caption') }}
)

SELECT
    video_id,
    manual_cover_text,
    caption,
    -- Remove all brackets and replace commas with spaces
    REGEXP_REPLACE(topic_tag, '\[|\]', '', 'g') AS topic_tag_cleaned,
    -- first_level_category_name,
    -- second_level_category_name,
    -- third_level_category_name
FROM source_data