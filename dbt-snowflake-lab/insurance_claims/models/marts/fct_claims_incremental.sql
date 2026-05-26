{{
    config(
        materialized='incremental',
        unique_key='claim_id',
        incremental_strategy='merge'
    )
}}

WITH new_claims AS (
    SELECT
        claim_id,
        claim_date,
        claim_amount,
        claim_type,
        claim_status,
        policy_id,
        customer_id,
        loaded_at
    FROM {{ ref('stg_claims') }}

    {% if is_incremental() %}
        -- Only rows newer than what we already have
        WHERE loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})
    {% endif %}
)

SELECT
    c.claim_id,
    c.claim_date,
    c.claim_amount,
    c.claim_type,
    c.claim_status,
    c.policy_id,
    p.policy_type,
    p.premium_amount,
    c.customer_id,
    cu.full_name AS customer_name,
    cu.state_code,
    c.loaded_at,
    DATE_TRUNC('month', c.claim_date) AS claim_month,
    CURRENT_TIMESTAMP() AS dbt_loaded_at
FROM new_claims c
LEFT JOIN {{ ref('stg_policies') }} p ON c.policy_id = p.policy_id
LEFT JOIN {{ ref('stg_customers') }} cu ON c.customer_id = cu.customer_id