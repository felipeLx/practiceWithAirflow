{% docs stg_customers %}
Cleaned customer records from raw source.

## Business Rules
- `full_name` = concatenation of first_name + last_name
- `customer_since` = original registration date

## Source
Raw data from `raw_insurance.raw_customers`
{% enddocs %}