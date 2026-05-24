WITH source AS (
    SELECT * FROM {{ source('raw_insurance', 'raw_claims') }}
)

SELECT
    claim_id,
    policy_id,
    claim_date,
    claim_amount,
    LOWER(claim_type) AS claim_type,
    LOWER(claim_status) AS claim_status,
    description,
    filed_by AS customer_id,
    created_at,
    loaded_at
FROM source