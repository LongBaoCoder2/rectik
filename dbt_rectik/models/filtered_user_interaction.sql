WITH filtered_interaction AS (
    SELECT user_id,
    FROM {{ ref('user_interaction_staging') }}
    GROUP BY user_id
    HAVING COUNT(*) >= 5
)

SELECT ui.*
FROM {{ ref('user_interaction_staging') }} as ui
JOIN filtered_interaction as fi
    ON ui.user_id = fi.user_id
ORDER BY ui.user_id, ui.date