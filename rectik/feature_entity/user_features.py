from datetime import timedelta
from feast import Entity, Field, FeatureView, ValueType
from feast.types import Int32
from feast.infra.offline_stores.file_source import FileSource

user_features = FileSource(
    path="/rectik/feast_repo/feature_repo/data/user_features.parquet",
    timestamp_field="datetime",
    created_timestamp_column="created",
)

user = Entity(name="user_id", value_type=ValueType.INT32, join_keys=["user_id"])

user_features_view = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(0),
    schema=[
        Field(name="onehot_feat0", dtype=Int32),
        Field(name="onehot_feat1", dtype=Int32),
        Field(name="onehot_feat2", dtype=Int32),
        Field(name="onehot_feat3", dtype=Int32),
        Field(name="onehot_feat4", dtype=Int32),
        Field(name="onehot_feat5", dtype=Int32),
        Field(name="onehot_feat6", dtype=Int32),
        Field(name="onehot_feat7", dtype=Int32),
        Field(name="onehot_feat8", dtype=Int32),
        Field(name="onehot_feat9", dtype=Int32),
        Field(name="onehot_feat10", dtype=Int32),
        Field(name="onehot_feat11", dtype=Int32),
        Field(name="onehot_feat12", dtype=Int32),
        Field(name="onehot_feat13", dtype=Int32),
        Field(name="onehot_feat14", dtype=Int32),
        Field(name="onehot_feat15", dtype=Int32),
        Field(name="onehot_feat16", dtype=Int32),
        Field(name="onehot_feat17", dtype=Int32),
        Field(name="is_lowactive_period", dtype=Int32),
        Field(name="is_live_streamer", dtype=Int32),
        Field(name="is_video_author", dtype=Int32),
        Field(name="follow_user_num_range", dtype=Int32),
        Field(name="fans_user_num_range", dtype=Int32),
        Field(name="friend_user_num_range", dtype=Int32),
        Field(name="register_days_range", dtype=Int32),
    ],
    online=True,
    source=user_features,
    tags=dict(),
)
