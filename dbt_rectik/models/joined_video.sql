{{ 
    config(materialized='external', 
           location='../data/video.parquet')
}}

SELECT 
    vs.*,
    vc.*,
    fi.*,
    fs.*
FROM 
    {{ ref("video_staging") }} as vs

JOIN 
    {{ ref("video_caption_staging") }} as vc
ON 
    vs.video_id = vc.video_id

JOIN 
    {{ ref("filtered_video_interaction") }} as fi
ON 
    vs.video_id = fi.video_id

JOIN 
    {{ ref("filtered_video_statistic") }} as fs
ON 
    vs.video_id = fs.video_id
