{{ 
    config(materialized='external', 
           location='../data/user.parquet')
}}


SELECT 
    uo.user_id, 
    uo.onehot_feat0::integer AS onehot_feat0,
    uo.onehot_feat1::integer AS onehot_feat1,
    uo.onehot_feat2::integer AS onehot_feat2,
    uo.onehot_feat3::integer AS onehot_feat3,
    uo.onehot_feat4::integer AS onehot_feat4,  
    uo.onehot_feat5::integer AS onehot_feat5,
    uo.onehot_feat6::integer AS onehot_feat6,
    uo.onehot_feat7::integer AS onehot_feat7,
    uo.onehot_feat8::integer AS onehot_feat8,
    uo.onehot_feat9::integer AS onehot_feat9,
    uo.onehot_feat10::integer AS onehot_feat10,
    uo.onehot_feat11::integer AS onehot_feat11,
    uo.onehot_feat12::integer AS onehot_feat12, 
    uo.onehot_feat13::integer AS onehot_feat13, 
    uo.onehot_feat14::integer AS onehot_feat14, 
    uo.onehot_feat15::integer AS onehot_feat15, 
    uo.onehot_feat16::integer AS onehot_feat16, 
    uo.onehot_feat17::integer AS onehot_feat17, 
    us.is_lowactive_period,
    us.is_live_streamer,
    us.is_video_author,
    us.follow_user_num_range,
    us.fans_user_num_range,
    us.friend_user_num_range,
    us.register_days_range,
FROM 
    {{ ref("user_staging") }} as us

JOIN 
    {{ ref("user_onehot_features_staging") }} as uo
ON
    us.user_id = uo.user_id
