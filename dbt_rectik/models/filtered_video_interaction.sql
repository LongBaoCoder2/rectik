SELECT vi.*
FROM {{ ref("video_interaction_staging") }} as vi
WHERE vi.date >= ALL(SELECT vi1.date
                    FROM {{ ref("video_interaction_staging") }} as vi1
                    WHERE vi.video_id = vi1.video_id)
    