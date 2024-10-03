WITH source_data AS (
    SELECT *
    FROM {{ source('postgres_database', 'user_interaction') }}
)

SELECT
    user_id,
    video_id,
    play_duration,
    time as date
FROM source_data