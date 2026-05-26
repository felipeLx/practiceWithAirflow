WITH claims AS (
    SELECT * FROM {{ ref('stg_claims') }}
),

policies AS (
    SELECT * FROM {{ ref('stg_policies') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
)

SELECT
    c.claim_id,
    c.claim_date,
    c.claim_amount,
    c.claim_type,
    c.claim_status,
    p.policy_id,
    p.policy_type,
    p.premium_amount,
    p.coverage_amount,
    p.status AS policy_status,
    cu.customer_id,
    cu.full_name AS customer_name,
    cu.state_code,
    -- Business logic: claim ratio
    ROUND(c.claim_amount / NULLIF(p.coverage_amount, 0) * 100, 2) AS claim_coverage_ratio
FROM claims c
LEFT JOIN policies p ON c.policy_id = p.policy_id
LEFT JOIN customers cu ON c.customer_id = cu.customer_id