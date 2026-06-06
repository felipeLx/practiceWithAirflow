from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

DBT_PROJECT_PATH = "/usr/local/airflow/dags/dbt/insurance_claims"
DBT_PROFILES_DIR = "/usr/local/airflow/dags/dbt"
SNOWFLAKE_CONN_ID = "snowflake_default"

# ============================================================
# CALLBACK FUNCTIONS
# ============================================================

def notify_on_failure(context):
    """Send alert when task fails."""
    task = context['task_instance']
    dag_id = context['dag'].dag_id
    error = context.get('exception', 'Unknown')
    print(f"ALERT: {dag_id}.{task.task_id} FAILED. Error: {error}")
    # In production: send Slack/email/PagerDuty here

default_args = {
    'owner': 'data_platform',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': notify_on_failure,  # alert function
}



# ============================================================
# PRE-CHECK: Is source data ready? Avoid wasting compute
# ============================================================

def check_source_freshness(**context):
    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    ti = context['ti']  # task instance — needed for xcom

    sources = ['raw_customers', 'raw_policies', 'raw_claims']
    has_new_data = False
    source_stats = {}

    for table in sources:
        result = hook.get_first(f"""
            SELECT COUNT(*) 
            FROM RAW.{table}
            WHERE loaded_at > DATEADD('day', -1, CURRENT_TIMESTAMP())
        """)
        row_count = result[0]
        source_stats[table] = row_count
        if row_count > 0:
            has_new_data = True

    # Push small metadata via XCom
    ti.xcom_push(key='source_stats', value=source_stats)
    ti.xcom_push(key='has_new_data', value=has_new_data)

    if has_new_data:
        return 'source_row_count'
    else:
        return 'skip_no_new_data'


def check_source_row_count(**context):
    ti = context['ti']

    # Pull XCom from previous task
    source_stats = ti.xcom_pull(task_ids='check_source_freshness', key='source_stats')
    print(f"Source stats from previous task: {source_stats}")

    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    
    checks = {
        'raw_customers': {'min_rows': 5, 'max_rows': 10000000},
        'raw_policies': {'min_rows': 5, 'max_rows': 50000000},
        'raw_claims': {'min_rows': 5, 'max_rows': 100000000},
    }

    total_rows = {}
    for table, limits in checks.items():
        result = hook.get_first(f"SELECT COUNT(*) FROM RAW.{table}")
        count = result[0]
        total_rows[table] = count

        if count < limits['min_rows']:
            raise ValueError(f"{table}: {count} rows (min: {limits['min_rows']})")
        if count > limits['max_rows']:
            raise ValueError(f"{table}: {count} rows (max: {limits['max_rows']})")

    # Push summary for downstream tasks
    ti.xcom_push(key='total_rows', value=total_rows)
    ti.xcom_push(key='validation_status', value='passed')


def validate_marts_quality(**context):
    ti = context['ti']
    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)

    checks = [
        {'name': 'no_null_ids', 'sql': "SELECT COUNT(*) FROM MARTS.fct_claims WHERE claim_id IS NULL", 'max': 0},
        {'name': 'positive_amounts', 'sql': "SELECT COUNT(*) FROM MARTS.fct_claims WHERE claim_amount <= 0", 'max': 0},
    ]

    results = {}
    failures = []
    for check in checks:
        result = hook.get_first(check['sql'])
        fail_count = result[0]
        status = 'PASS' if fail_count <= check['max'] else 'FAIL'
        results[check['name']] = {'status': status, 'failures': fail_count}
        if status == 'FAIL':
            failures.append(check['name'])

    # Push quality report via XCom
    ti.xcom_push(key='quality_report', value=results)
    ti.xcom_push(key='quality_status', value='failed' if failures else 'passed')

    if failures:
        raise ValueError(f"Quality FAILED: {failures}")

# ============================================================
# QUARANTINE: Handle bad data for investigation
# ============================================================

QUARANTINE_BAD_CLAIMS = """
    CREATE TABLE IF NOT EXISTS RAW.quarantine_claims (
        claim_id VARCHAR, policy_id VARCHAR, claim_date DATE,
        claim_amount NUMBER(12,2), claim_type VARCHAR, claim_status VARCHAR,
        description VARCHAR, filed_by VARCHAR, created_at TIMESTAMP,
        loaded_at TIMESTAMP, quarantined_at TIMESTAMP, quarantine_reason VARCHAR
    );

    INSERT INTO RAW.quarantine_claims
    SELECT *, CURRENT_TIMESTAMP(), 'negative_amount'
    FROM RAW.raw_claims WHERE claim_amount < 0
    UNION ALL
    SELECT *, CURRENT_TIMESTAMP(), 'future_date'
    FROM RAW.raw_claims WHERE claim_date > CURRENT_DATE()
    UNION ALL
    SELECT c.*, CURRENT_TIMESTAMP(), 'orphan_policy'
    FROM RAW.raw_claims c
    LEFT JOIN RAW.raw_policies p ON c.policy_id = p.policy_id
    WHERE p.policy_id IS NULL;
"""

REMOVE_QUARANTINED_FROM_STAGING = """
    DELETE FROM RAW.raw_claims
    WHERE claim_id IN (SELECT claim_id FROM RAW.quarantine_claims);
"""

# ============================================================
# DAG DEFINITION
# ============================================================

with DAG(
    dag_id='insurance_dbt_pipeline',
    default_args=default_args,
    description='Production insurance pipeline with quality gates',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['insurance', 'dbt', 'snowflake', 'production'],
    doc_md="""
    ## Insurance Claims Pipeline
    
    **Pre-checks** → **Quarantine bad data** → **dbt run** → **Post-checks**
    
    Fails fast if source data has issues. Quarantines bad records
    for investigation instead of breaking the pipeline.
    """,
) as dag:

    # ---- PRE-CHECKS ----

    check_freshness = BranchPythonOperator(
        task_id='check_source_freshness',
        python_callable=check_source_freshness,
    )

    skip_no_new_data = EmptyOperator(
        task_id='skip_no_new_data',
    )

    source_row_count = PythonOperator(
        task_id='source_row_count',
        python_callable=check_source_row_count,
    )

    # ---- QUARANTINE BAD DATA ----

    quarantine_bad_records = SQLExecuteQueryOperator(
        task_id='quarantine_bad_records',
        sql=QUARANTINE_BAD_CLAIMS,
        conn_id=SNOWFLAKE_CONN_ID,
    )

    remove_quarantined = SQLExecuteQueryOperator(
        task_id='remove_quarantined',
        sql=REMOVE_QUARANTINED_FROM_STAGING,
        conn_id=SNOWFLAKE_CONN_ID,
    )

    # ---- DBT PIPELINE ----

    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command=f'cd {DBT_PROJECT_PATH} && dbt seed --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_snapshot = BashOperator(
        task_id='dbt_snapshot',
        bash_command=f'cd {DBT_PROJECT_PATH} && dbt snapshot --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'cd {DBT_PROJECT_PATH} && dbt run --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_PROJECT_PATH} && dbt test --profiles-dir {DBT_PROFILES_DIR}',
    )

    # ---- POST-CHECKS ----

    validate_quality = PythonOperator(
        task_id='validate_marts_quality',
        python_callable=validate_marts_quality,
    )

    pipeline_complete = EmptyOperator(
        task_id='pipeline_complete',
        trigger_rule='none_failed_min_one_success',
    )

    # ---- DAG FLOW ----

    # Pre-check: is data fresh?
    check_freshness >> [source_row_count, skip_no_new_data]

    # If fresh: validate → quarantine → dbt → quality check
    source_row_count >> quarantine_bad_records >> remove_quarantined  >> dbt_seed >> dbt_snapshot >> dbt_run >> dbt_test >> validate_quality >> pipeline_complete

    # If not fresh: skip
    skip_no_new_data >> pipeline_complete