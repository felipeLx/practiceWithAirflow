WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

policy_metrics AS (
    SELECT
        customer_id,
        COUNT(*) AS total_policies,
        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_policies,
        SUM(premium_amount) AS total_premium
    FROM {{ ref('stg_policies') }}
    GROUP BY customer_id
),

claim_metrics AS (
    SELECT
        customer_id,
        COUNT(*) AS total_claims,
        SUM(claim_amount) AS total_claim_amount,
        AVG(claim_amount) AS avg_claim_amount
    FROM {{ ref('stg_claims') }}
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.state_code,
    c.customer_since,
    COALESCE(p.total_policies, 0) AS total_policies,
    COALESCE(p.active_policies, 0) AS active_policies,
    COALESCE(p.total_premium, 0) AS total_premium,
    COALESCE(cm.total_claims, 0) AS total_claims,
    COALESCE(cm.total_claim_amount, 0) AS total_claim_amount,
    COALESCE(cm.avg_claim_amount, 0) AS avg_claim_amount
FROM customers c
LEFT JOIN policy_metrics p ON c.customer_id = p.customer_id
LEFT JOIN claim_metrics cm ON c.customer_id = cm.customer_id