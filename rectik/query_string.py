VIDEO_FEATURES_QUERY = """
SELECT 
    video_id, 
    author_id, 
    upload_dt, 
    visible_status, 
    video_duration, 
    video_width, 
    video_height, 
    manual_cover_text, 
    caption, 
    topic_tag_cleaned, 
    date as statistic_date, 
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
    show_cnt, 
    show_user_num, 
    play_cnt, 
    play_user_num, 
    play_duration as total_play_duration, 
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
FROM
    read_parquet('{}')               -- Parquet data file
    {}                               -- Sampling method
ORDER BY
    video_id ASC
"""



USER_FEATURE_QUERY = """
SELECT 
    user_id, 
    onehot_feat0, 
    onehot_feat1, 
    onehot_feat2, 
    onehot_feat3, 
    onehot_feat4, 
    onehot_feat5, 
    onehot_feat6, 
    onehot_feat7, 
    onehot_feat8, 
    onehot_feat9, 
    onehot_feat10, 
    onehot_feat11, 
    onehot_feat12, 
    onehot_feat13, 
    onehot_feat14, 
    onehot_feat15, 
    onehot_feat16, 
    onehot_feat17, 
    is_lowactive_period, 
    is_live_streamer, 
    is_video_author, 
    follow_user_num_range, 
    fans_user_num_range, 
    friend_user_num_range, 
    register_days_range
FROM
    read_parquet('{}')               -- Parquet data file
    {}                               -- Sampling method
ORDER BY
    user_id ASC
"""


USER_ITEM_INTERACTION_QUERY = """
SELECT 
    user_id, 
    video_id, 
    play_duration, 
    date as interaction_date
FROM
    read_parquet('{}')               -- Parquet data file
    {}                               -- Sampling method
ORDER BY
    user_id, date ASC
"""