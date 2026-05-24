## Steps to follow:
# 1. Set pyenv path (add to your $PROFILE so it persists)
$env:PYENV = "$env:USERPROFILE\.pyenv\pyenv-win"
$env:PATH = "$env:PYENV\bin;$env:PYENV\shims;$env:PATH"

# 2. Go to project dir, set python version
cd C:\Users\felip\Workspace\dbt-snowflake-lab
pyenv local 3.12.10

# 3. Create venv + activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 4. Install dbt
pip install dbt-snowflake

# 5. Init project
dbt init insurance_claims
# Pick snowflake when prompted

# In project dir with venv active
cd insurance_claims

# 1. First create database in Snowflake
# Run this in Snowflake worksheet:
# CREATE DATABASE IF NOT EXISTS INSURANCE_DB;
# CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH WITH WAREHOUSE_SIZE='XSMALL' AUTO_SUSPEND=60;

# 2. Load seed data
dbt seed

# 3. Run models (builds DAG automatically)
dbt run

# 4. Run tests
dbt test

# 5. Generate docs
dbt docs generate
dbt docs serve