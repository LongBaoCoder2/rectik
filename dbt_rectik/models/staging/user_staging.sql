WITH source_data AS (
    SELECT *
    FROM {{ source('postgres_database', 'user') }}
)


SELECT
    user_id,
    is_lowactive_period,
    is_live_streamer,
    is_video_author,
    follow_user_num_range,
    fans_user_num_range,
    friend_user_num_range,
    register_days_range
FROM source_data
