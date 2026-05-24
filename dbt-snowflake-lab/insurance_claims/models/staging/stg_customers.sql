WITH source AS (
    SELECT * FROM {{ source('raw_insurance', 'raw_customers') }}
)

SELECT
    customer_id,
    TRIM(first_name || ' ' || last_name) AS full_name,
    email,
    state_code,
    date_of_birth,
    created_at AS customer_since,
    loaded_at
FROM source