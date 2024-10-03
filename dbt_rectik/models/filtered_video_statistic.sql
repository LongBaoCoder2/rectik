SELECT vs.*
FROM {{ ref("video_statistic_staging") }} vs
WHERE vs.date >= ALL(SELECT vs1.date
                     FROM {{ ref("video_statistic_staging") }} vs1
                     WHERE vs.video_id = vs1.video_id)