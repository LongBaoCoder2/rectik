WITH source_data AS (
    SELECT *
    FROM {{ source('postgres_database', 'video_statistic') }}
)

SELECT
    video_id,
    date,
    show_cnt,
    show_user_num,
    play_cnt,
    play_user_num,
    play_duration,
    complete_play_cnt,
    complete_play_user_num,
    valid_play_cnt,
    valid_play_user_num,
    long_time_play_cnt,
    long_time_play_user_num,
    short_time_play_cnt,
    short_time_play_user_num,
    play_progress,
    comment_stay_duration
FROM source_data
