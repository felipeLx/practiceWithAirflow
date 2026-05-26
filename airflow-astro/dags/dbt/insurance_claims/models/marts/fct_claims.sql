SELECT
    claim_id,
    claim_date,
    claim_amount,
    claim_type,
    claim_status,
    policy_id,
    policy_type,
    customer_id,
    customer_name,
    state_code,
    claim_coverage_ratio,
    -- Date dimensions for BI
    DATE_TRUNC('month', claim_date) AS claim_month,
    YEAR(claim_date) AS claim_year
FROM {{ ref('int_claims_enriched') }}