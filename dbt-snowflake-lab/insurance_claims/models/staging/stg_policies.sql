WITH source AS (
    SELECT * FROM {{ source('raw_insurance', 'raw_policies') }}
)

SELECT
    policy_id,
    customer_id,
    LOWER(policy_type) AS policy_type,
    premium_amount,
    coverage_amount,
    start_date,
    end_date,
    LOWER(status) AS status,
    created_at,
    loaded_at
FROM source