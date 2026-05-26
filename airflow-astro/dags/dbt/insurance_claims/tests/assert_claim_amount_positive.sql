-- Singular test: all claim amounts must be positive
SELECT
    claim_id,
    claim_amount
FROM {{ ref('stg_claims') }}
WHERE claim_amount <= 0