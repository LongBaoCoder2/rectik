{{ 
    config(materialized='external', 
           location='../data/user_item.parquet')
}}

SELECT 
    fi.*,
    vs.video_duration,
    fi.play_duration / vs.video_duration AS play_ratio
FROM 
    {{ ref("filtered_user_interaction") }} as fi

JOIN 
    {{ ref("video_staging") }} as vs
ON 
    vs.video_id = fi.video_id