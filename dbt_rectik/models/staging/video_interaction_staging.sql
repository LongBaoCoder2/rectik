WITH source_data AS (
    SELECT *
    FROM {{ source('postgres_database', 'video_interaction') }}
)

SELECT
    video_id,
    date,
    like_cnt,
    click_like_cnt,
    double_click_cnt,
    cancel_like_cnt,
    comment_cnt,
    direct_comment_cnt,
    reply_comment_cnt,
    delete_comment_cnt,
    comment_like_cnt,
    follow_cnt,
    cancel_follow_cnt,
    share_cnt,
    download_cnt,
    report_cnt,
    reduce_similar_cnt,
    collect_cnt,
    cancel_collect_cnt,
FROM source_data
