{% snapshot snap_policies %}

{{
    config(
        target_database='INSURANCE_DB',
        target_schema='SNAPSHOTS',
        unique_key='policy_id',
        strategy='check',
        check_cols=['status', 'premium_amount']
    )
}}

SELECT
    policy_id,
    customer_id,
    policy_type,
    premium_amount,
    coverage_amount,
    start_date,
    end_date,
    status,
    loaded_at
FROM {{ source('raw_insurance', 'raw_policies') }}

{% endsnapshot %}