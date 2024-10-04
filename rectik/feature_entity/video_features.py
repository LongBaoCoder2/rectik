from datetime import timedelta
from feast import Entity, Field, FeatureView, ValueType
from feast.types import Int32, Float32
from feast.infra.offline_stores.file_source import FileSource

# Define the source of video features
video_features_source = FileSource(
    path="/rectik/feast_repo/feature_repo/data/video_features.parquet",
    timestamp_field="datetime",
    created_timestamp_column="created",
)

# Define the Entity for videos
video = Entity(name="video_id", value_type=ValueType.INT32, join_keys=["video_id"])

# Define the FeatureView for video features
video_features_view = FeatureView(
    name="video_features",
    entities=[video],
    ttl=timedelta(0),
    schema=[
        Field(name="video_duration", dtype=Float32),
        Field(name="total_play_duration", dtype=Float32),
        Field(name="like_cnt", dtype=Float32),
        Field(name="click_like_cnt", dtype=Float32),
        Field(name="double_click_cnt", dtype=Float32),
        Field(name="cancel_like_cnt", dtype=Float32),
        Field(name="comment_cnt", dtype=Float32),
        Field(name="direct_comment_cnt", dtype=Float32),
        Field(name="reply_comment_cnt", dtype=Float32),
        Field(name="delete_comment_cnt", dtype=Float32),
        Field(name="comment_like_cnt", dtype=Float32),
        Field(name="follow_cnt", dtype=Float32),
        Field(name="cancel_follow_cnt", dtype=Float32),
        Field(name="share_cnt", dtype=Float32),
        Field(name="download_cnt", dtype=Float32),
        Field(name="report_cnt", dtype=Float32),
        Field(name="reduce_similar_cnt", dtype=Float32),
        Field(name="collect_cnt", dtype=Float32),
        Field(name="cancel_collect_cnt", dtype=Float32),
        Field(name="show_cnt", dtype=Float32),
        Field(name="show_user_num", dtype=Float32),
        Field(name="play_cnt", dtype=Float32),
        Field(name="play_user_num", dtype=Float32),
        Field(name="complete_play_cnt", dtype=Float32),
        Field(name="complete_play_user_num", dtype=Float32),
        Field(name="valid_play_cnt", dtype=Float32),
        Field(name="valid_play_user_num", dtype=Float32),
        Field(name="long_time_play_cnt", dtype=Float32),
        Field(name="long_time_play_user_num", dtype=Float32),
        Field(name="short_time_play_cnt", dtype=Float32),
        Field(name="short_time_play_user_num", dtype=Float32),
        Field(name="comment_stay_duration", dtype=Float32),
    ],
    online=True,
    source=video_features_source,
    tags=dict(),
)
