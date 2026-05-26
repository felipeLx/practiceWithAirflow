# dbt + Snowflake Learning Lab

## Project Overview
Insurance claims data pipeline built with dbt + Snowflake.
Domain: insurance policies, customers, and claims — modeled as dimensional schema (fact + dimension tables).

---

## Setup

### Prerequisites
- Python 3.12 (dbt incompatible with 3.14 — `mashumaro` library breaks)
- pyenv-win for Python version management
- Snowflake trial account (30 days, $400 credit)

### Installation
```powershell
# 1. Set pyenv path (add to $PROFILE for persistence)
$env:PYENV = "$env:USERPROFILE\.pyenv\pyenv-win"
$env:PATH = "$env:PYENV\bin;$env:PYENV\shims;$env:PATH"

# 2. Set Python version for project
cd C:\Users\felip\Workspace\practiceWithAirflow\dbt-snowflake-lab
pyenv local 3.12.10

# 3. Create venv + activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 4. Install dbt-snowflake adapter
pip install dbt-snowflake

# 5. Init project (pick snowflake when prompted)
dbt init insurance_claims
```

### Snowflake Setup (run in Snowsight worksheet, NOT Databricks/DBeaver)
```sql
CREATE DATABASE IF NOT EXISTS INSURANCE_DB;
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;
```

> **Lesson learned:** `CREATE WAREHOUSE` has NO `WITH` keyword. Also Snowflake SQL != Databricks SQL != PostgreSQL SQL. Always check which engine you're connected to. Error `SQLSTATE: 42601` = PostgreSQL family, not Snowflake.

### profiles.yml (~/.dbt/profiles.yml)
```yaml
insurance_claims:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "ORG-ACCOUNT"     # NO dots, NO tabs, NO slashes
      user: "USERNAME"
      password: "xxx"            # For learning only. Prod: use env_var()
      role: ACCOUNTADMIN
      warehouse: COMPUTE_WH
      database: INSURANCE_DB
      schema: RAW
      threads: 4
```

> **Lesson learned:** Account identifier must have NO dots/tabs/slashes. Tab character (`\t`) in YAML string caused `Invalid account identifier` error. Always check for invisible characters.

> **Prod best practice:** Use environment variables instead of plaintext credentials:
> ```yaml
> account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
> password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
> ```

---

## Running the Project

```powershell
cd insurance_claims

# Load CSV seed data into Snowflake
dbt seed

# Compile Jinja to SQL (check for errors without running)
dbt compile

# Run all models (creates views/tables in Snowflake)
dbt run

# Run all tests (generic from YML + singular from tests/)
dbt test

# Generate and serve documentation
dbt docs generate
dbt docs serve
```

---

## Project Structure

```
insurance_claims/
├── dbt_project.yml              # Master config: paths, materializations per folder
├── profiles.yml                 # Connection config (lives in ~/.dbt/, NOT here)
│
├── seeds/                       # CSV files → loaded directly into Snowflake via dbt seed
│   ├── raw_customers.csv
│   ├── raw_policies.csv
│   └── raw_claims.csv
│
├── models/
│   ├── staging/                 # 1:1 with source. Clean, rename, cast only
│   │   ├── _stg_sources.yml    # Source definitions (where raw data lives)
│   │   ├── _stg_models.yml     # Model docs + tests
│   │   ├── stg_customers.sql
│   │   ├── stg_policies.sql
│   │   └── stg_claims.sql
│   │
│   ├── intermediate/            # Business logic, joins. Not exposed to BI
│   │   ├── _int_models.yml
│   │   └── int_claims_enriched.sql
│   │
│   └── marts/                   # Final tables for BI/analytics consumers
│       ├── _marts_models.yml
│       ├── fct_claims.sql       # Fact table (events/transactions)
│       ├── dim_customers.sql    # Dimension table (entity + metrics)
│       └── dim_policies.sql     # Dimension table
│
├── macros/                      # Reusable SQL/Jinja functions
│   ├── _macros.yml              # Macro documentation
│   ├── cents_to_dollars.sql
│   └── generate_schema_name.sql # Override for schema naming
│
├── snapshots/                   # SCD Type 2 tracking
│   └── snap_policies.sql
│
├── tests/                       # Custom singular tests (SQL that returns failing rows)
│   └── assert_claim_amount_positive.sql
│
└── analyses/                    # Ad-hoc queries (compiled but not materialized)
    └── monthly_claims_report.sql
```

> **Convention:** `_` prefix on YML files keeps them at top of folder listing. Not required by dbt.

---

## Key Concepts Learned

### 1. Materializations (dbt_project.yml)
```yaml
models:
  insurance_claims:
    staging:
      +materialized: view        # Cheap, always fresh, no storage cost
    intermediate:
      +materialized: ephemeral   # CTE injected into downstream SQL, no table created
    marts:
      +materialized: table       # Persisted table, fast for BI queries
```

| Type | Creates | When to use |
|------|---------|------------|
| `view` | SQL view | Staging layer, small data |
| `table` | Physical table | Marts, BI-facing, large data |
| `ephemeral` | Nothing (CTE) | Helper logic, avoid table sprawl |
| `incremental` | Table + merge | Large tables, only process new rows |

> **`+` prefix in YAML config** = applies to folder AND all subfolders.

### 2. ref() and source() — DAG Building
```sql
{{ source('raw_insurance', 'raw_customers') }}  -- points to raw table (from _stg_sources.yml)
{{ ref('stg_customers') }}                       -- points to another dbt model
```
- `ref()` builds the DAG automatically — dbt knows execution order from dependencies
- `source()` is abstraction layer — if raw table name changes, update ONE yml file, not 20 models

### 3. Schema Naming — generate_schema_name Override
**Problem:** dbt default = `target_schema + '_' + custom_schema` → `RAW_RAW`, `RAW_STAGING`

**Fix:** Override `generate_schema_name` macro to use custom_schema directly:
```sql
{% macro generate_schema_name(custom_schema_name, node) %}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{% endmacro %}
```

> **Interview gold:** "How does dbt handle schema names?" — Top 5 dbt interview question. Explain default behavior + override.

### 4. Macros — Reusable SQL Functions
- Defined in `macros/` folder with `{% macro name(args) %}`
- Called in models with `{{ macro_name(args) }}`
- Compiled to pure SQL before sending to Snowflake — Snowflake never sees Jinja
- `ref()`, `source()`, `config()` are all built-in macros

```sql
-- Definition (macros/cents_to_dollars.sql)
{% macro cents_to_dollars(column_name) %}
    ROUND({{ column_name }} / 100.0, 2)
{% endmacro %}

-- Usage (any model)
SELECT {{ cents_to_dollars('amount_cents') }} AS amount_dollars
```

### 5. Tests
| Type | Where | How |
|------|-------|-----|
| Generic (YML) | `_stg_models.yml` | `unique`, `not_null`, `relationships`, `accepted_values` |
| Singular (SQL) | `tests/` folder | SQL query that returns FAILING rows (0 rows = pass) |
| Package | `dbt_expectations` | Advanced tests from community packages |

> **dbt 1.11 change:** `relationships` and `accepted_values` args must be nested under `arguments:` key.

### 6. YAML Syntax — Common Mistakes
```yaml
# ARRAY (list) — dash + space + value
data_tests:
  - unique        # ✅ correct
  - not_null      # ✅ correct

# NOT this (dict, not array):
data_tests:
  unique          # ❌ wrong — no dash
  not_null        # ❌ wrong

# NOT this (double dash):
data_tests:
  --unique        # ❌ wrong — YAML document marker, not list
```

### 7. Snowflake Case Sensitivity
```sql
CREATE DATABASE INSURANCE_DB;     -- stored as INSURANCE_DB (unquoted = UPPERCASE)
CREATE DATABASE "insurance_db";   -- stored as insurance_db (quoted = exact case)
```
Always use UPPERCASE unquoted identifiers in Snowflake. Quoted lowercase causes matching issues with dbt.

### 8. Snowflake Cost Management
- `AUTO_SUSPEND = 60` — warehouse suspends after 60s idle, billing stops
- `AUTO_RESUME = TRUE` — wakes automatically on query
- XSMALL = cheapest size (~$2/hr active)
- Suspended warehouse = $0 cost
- Trial: $400 credit, plenty for learning

---

## Naming Conventions — Medallion vs dbt

Same architecture, different naming:

| Medallion (Databricks) | dbt Convention | Purpose |
|------------------------|---------------|---------|
| Bronze | Raw / Sources | Raw data, no transforms |
| Silver | Staging (`stg_`) | Clean, rename, cast, 1:1 with source |
| Silver | Intermediate (`int_`) | Business logic, joins |
| Gold | Marts (`fct_`/`dim_`) | Final tables for BI |

dbt prefix conventions:
- `raw_` — source tables
- `stg_` — staging (1:1 clean)
- `int_` — intermediate (business joins)
- `fct_` — fact tables (events/transactions)
- `dim_` — dimension tables (entities)
- `snap_` — snapshots (SCD Type 2)
- `rpt_` — reports/aggregations

> **Interview line:** "I've worked with both Medallion and dbt layered architecture — same concept, different naming. I adapt to team convention."

---

## How dbt Connects to Snowflake

```
profiles.yml (connection config)
       │
       ▼
snowflake-connector-python
       │
       ▼
Snowflake Account
       │
       ▼
dbt run → Jinja compiles to SQL → sent to Snowflake → CREATE VIEW/TABLE AS SELECT
```

dbt never stores data locally. All computation happens in Snowflake warehouse.

---

## Architecture: Airflow + dbt + Snowflake

```
Airflow (orchestrator — WHEN/ORDER)
   │
   ├── Extract Task (PythonOperator / API calls)
   │       ↓
   ├── Load Task (S3 → Snowflake COPY INTO)
   │       ↓
   ├── Transform Task (dbt run via Cosmos/BashOperator)
   │       ↓
   ├── Test Task (dbt test)
   │       ↓
   └── BI / downstream consumers
```

- **Airflow** = orchestrator (train conductor)
- **dbt** = transformer (train engine)
- **Snowflake** = compute + storage (railroad tracks)

---

## Next Steps
- [ ] Add incremental model (`fct_claims_incremental`)
- [ ] Add snapshot (SCD Type 2 for policy changes)
- [ ] Install dbt packages (`dbt_utils`, `dbt_expectations`)
- [ ] Build Airflow DAG with Cosmos integration
- [ ] CI/CD pipeline with Jenkins
- [ ] Snowflake Iceberg tables via dbt
