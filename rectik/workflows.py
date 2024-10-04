import nvtabular as nvt
from nvtabular import ops
from merlin.schema.tags import Tags
from merlin.dag.ops.subgraph import Subgraph


def cast_to_float32(col):
    return col.astype("float32")

user_workflow = Subgraph("user", (
    (["user_id"] >> ops.Categorify(dtype="int32") >> ops.TagAsUserID()) +
    ([
        "onehot_feat0", "onehot_feat1", "onehot_feat2", "onehot_feat3", 
        "onehot_feat5", "onehot_feat6", "onehot_feat7", "onehot_feat8", 
        "onehot_feat9", "onehot_feat10", "onehot_feat11", "onehot_feat4",
        "onehot_feat12", "onehot_feat13", "onehot_feat14", "onehot_feat15", 
        "onehot_feat16", "onehot_feat17",
        "is_lowactive_period", "is_live_streamer", "is_video_author",
        "follow_user_num_range", "fans_user_num_range", "friend_user_num_range", 
        "register_days_range"
    ]  >> ops.Categorify(dtype="int32") >> ops.TagAsUserFeatures())
) )


video_workflow = Subgraph("video", (
    (["video_id"]  >> ops.TagAsItemID()) + 
    ([
        "like_cnt", "click_like_cnt", "double_click_cnt", "cancel_like_cnt", 
        "comment_cnt", "direct_comment_cnt", "reply_comment_cnt", 
        "delete_comment_cnt", "comment_like_cnt", "follow_cnt", 
        "cancel_follow_cnt", "share_cnt", "download_cnt", "report_cnt", 
        "reduce_similar_cnt", "collect_cnt", "cancel_collect_cnt", "show_cnt", 
        "show_user_num", "play_cnt", "play_user_num", 
        "complete_play_cnt", "complete_play_user_num", "valid_play_cnt", 
        "valid_play_user_num", "long_time_play_cnt", "long_time_play_user_num", 
        "short_time_play_cnt", "short_time_play_user_num", 
        "comment_stay_duration", "video_duration", "total_play_duration"
    ] >> ops.TagAsItemFeatures()) + 
    (["video_id"] >> ops.Categorify(dtype="int32")) +
    ([
        "video_duration", "total_play_duration"
    ] >> ops.LambdaOp(cast_to_float32) 
      >> ops.Normalize("float32")) +
    ([
        "like_cnt", "click_like_cnt", "double_click_cnt", "cancel_like_cnt", 
        "comment_cnt", "direct_comment_cnt", "reply_comment_cnt", 
        "delete_comment_cnt", "comment_like_cnt", "follow_cnt", 
        "cancel_follow_cnt", "share_cnt", "download_cnt", "report_cnt", 
        "reduce_similar_cnt", "collect_cnt", "cancel_collect_cnt", "show_cnt", 
        "show_user_num", "play_cnt", "play_user_num", 
        "complete_play_cnt", "complete_play_user_num", "valid_play_cnt", 
        "valid_play_user_num", "long_time_play_cnt", "long_time_play_user_num", 
        "short_time_play_cnt", "short_time_play_user_num", 
        "comment_stay_duration"
    ] >> ops.LambdaOp(cast_to_float32) 
      >> ops.Normalize("float32") )
))


interaction_workflow = (
    ([ "play_duration"] >> ops.LambdaOp(cast_to_float32) 
                        >> ops.Normalize("float32") 
                        >> ops.AddMetadata([Tags.REGRESSION, Tags.CONTINUOUS  , "target"]))
)

outputs = (user_workflow + video_workflow + interaction_workflow) >> ops.Dropna()