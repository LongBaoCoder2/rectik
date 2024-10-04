WITH source_data AS (
    SELECT *
    FROM {{ source('postgres_database', 'video') }}
)

SELECT
    video_id,
    author_id,
    upload_dt,
    visible_status, --  # Constraint: ['public', 'private', 'only friends']
    video_duration,
    video_width,
    video_height,
FROM source_data
