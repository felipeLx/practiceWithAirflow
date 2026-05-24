WITH policies AS (
    SELECT * FROM {{ ref('stg_policies') }}
),

claim_summary AS (
    SELECT
        policy_id,
        COUNT(*) AS claim_count,
        SUM(claim_amount) AS total_claimed
    FROM {{ ref('stg_claims') }}
    GROUP BY policy_id
)

SELECT
    p.policy_id,
    p.customer_id,
    p.policy_type,
    p.premium_amount,
    p.coverage_amount,
    p.start_date,
    p.end_date,
    p.status,
    COALESCE(cs.claim_count, 0) AS claim_count,
    COALESCE(cs.total_claimed, 0) AS total_claimed,
    -- Loss ratio: claims vs premium (interview question!)
    CASE 
        WHEN p.premium_amount > 0 
        THEN ROUND(COALESCE(cs.total_claimed, 0) / p.premium_amount, 2)
        ELSE 0 
    END AS loss_ratio
FROM policies p
LEFT JOIN claim_summary cs ON p.policy_id = cs.policy_id