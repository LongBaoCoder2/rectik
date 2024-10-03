WITH source_data AS (
    SELECT *
    FROM {{ source('postgres_database', 'user_onehot_features') }}
)

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
    onehot_feat17
FROM source_data
