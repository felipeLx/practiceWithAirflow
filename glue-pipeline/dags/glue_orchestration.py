"""
Airflow DAG: Orchestrate AWS Glue Jobs.

Architecture:
  Airflow = orchestrator ONLY. No SparkSession here. No heavy compute.
  Glue job script (jobs/process_claims.py) owns all Spark logic.

  DAG responsibility: trigger, monitor, gate, route, alert.
  Job responsibility: extract, validate, transform, load.

Flow:
  check_source_freshness → start_glue_job → quality_gate →
    → [pass] load_to_snowflake → update_tracking → done
    → [fail] quality_failed → update_tracking → done

In real AWS:
  - GlueJobOperator triggers job, GlueJobSensor monitors
  - SNS for alerts, DynamoDB for tracking
  - No PySpark code in DAG at all
"""
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ============================================================
# CONFIG
# ============================================================

GLUE_JOB_NAME = "process_claims"
S3_INPUT = "s3://insurance-raw/claims/"
S3_OUTPUT = "s3://insurance-processed/claims/"
S3_QUARANTINE = "s3://insurance-quarantine/claims/"
SNOWFLAKE_TABLE = "RAW.glue_claims"

# Local config — in prod these come from Glue job parameters or SSM
LOCAL_CONFIG = {
    "input_path": "data/raw/raw_claims.csv",
    "policies_path": "data/raw/raw_policies.csv",
    "output_path": "data/processed/claims.csv",
    "quarantine_path": "data/quarantine/claims.csv",
}

default_args = {
    "owner": "data_platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": lambda ctx: logger.error(
        "Task %s failed", ctx["task_instance"].task_id
    ),
}


# ============================================================
# TASK FUNCTIONS
# ============================================================

def check_source_freshness(**context):
    """
    Check if new data exists before starting expensive Glue job.

    In AWS: check S3 prefix for new files since last run.
    Uses Glue job bookmarks or S3 list + DynamoDB last_run timestamp.

    Returns task_id to branch to.
    """
    # In production:
    # import boto3
    # s3 = boto3.client('s3')
    # response = s3.list_objects_v2(
    #     Bucket='insurance-raw', Prefix='claims/',
    #     StartAfter=last_processed_key
    # )
    # has_new_data = response.get('KeyCount', 0) > 0

    # Simulated: always has data for demo
    has_new_data = True

    if has_new_data:
        logger.info("FRESHNESS: New data found — proceeding")
        return "start_glue_job"
    else:
        logger.info("FRESHNESS: No new data — skipping")
        return "skip_no_new_data"


def start_glue_job(**context):
    """
    Start Glue job and collect metrics.

    In AWS:
        GlueJobOperator(
            job_name='process_claims',
            script_args={'--input_path': 's3://...'},
        )
        # Metrics come from DynamoDB after job completes.

    Locally:
        Import run_job() — SparkSession created INSIDE the job, NOT here.
        DAG stays thin. Job is independently testable.
    """
    logger.info("Starting job: %s", GLUE_JOB_NAME)

    # In production: boto3 Glue client
    # import boto3
    # glue = boto3.client('glue')
    # response = glue.start_job_run(
    #     JobName=GLUE_JOB_NAME,
    #     Arguments={
    #         '--input_path': S3_INPUT,
    #         '--output_path': S3_OUTPUT,
    #         '--quarantine_path': S3_QUARANTINE,
    #     }
    # )
    # run_id = response['JobRunId']
    # # Then GlueJobSensor waits for completion
    # # Then read metrics from DynamoDB

    # Locally: call run_job() — all Spark logic lives in jobs/process_claims.py
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from jobs.process_claims import run_job

    metrics = run_job(LOCAL_CONFIG)
    
    # Calculate and push only what downstream tasks NEED
    input_rows = metrics.get("input_rows", 0)
    output_rows = metrics.get("output_rows", 0)
    quarantined = metrics.get("quarantined_rows", 0)
    quarantine_rate = quarantined / input_rows if input_rows > 0 else 0
    
    context["ti"].xcom_push(key="input_rows", value=input_rows)
    context["ti"].xcom_push(key="output_rows", value=output_rows)
    context["ti"].xcom_push(key="quarantine_rate", value=quarantine_rate)
    context["ti"].xcom_push(key="quarantine_reasons", value=str(metrics.get("quarantine_reasons", {})))
    
    logger.info("Job completed: input=%d output=%d quarantine_rate=%.1f%%",
                input_rows, output_rows, quarantine_rate * 100)

def quality_gate(**context):
    """Pull individual metrics, not dict."""
    quarantine_rate = context["ti"].xcom_pull(
        task_ids="start_glue_job", key="quarantine_rate"
    )
    output_rows = context["ti"].xcom_pull(
        task_ids="start_glue_job", key="output_rows"
    )
    
    if quarantine_rate is None or output_rows is None:
        logger.error("QUALITY: Missing metrics")
        return "quality_failed"
    
    logger.info("QUALITY: Quarantine rate=%.1f%% Output=%d rows",
                quarantine_rate * 100, output_rows)
    
    if quarantine_rate > 0.5:
        logger.warning("QUALITY: FAIL — quarantine rate %.1f%%", quarantine_rate * 100)
        return "quality_failed"
    
    if output_rows == 0:
        logger.warning("QUALITY: FAIL — zero output rows")
        return "quality_failed"
    
    logger.info("QUALITY: PASS")
    return "load_to_snowflake"

def load_to_snowflake(**context):
    """
    Load processed data to Snowflake.

    In production: Glue job writes directly, or COPY INTO from S3 stage.
    This task would run Snowflake SQL via SQLExecuteQueryOperator.
    """
    output_rows = context["ti"].xcom_pull(
        task_ids="start_glue_job", key="output_rows"
    )

    logger.info("SNOWFLAKE: Would load %d rows to %s", output_rows, SNOWFLAKE_TABLE)
    # In production:
    # COPY INTO RAW.glue_claims
    # FROM @insurance_stage/processed/claims/
    # FILE_FORMAT = (TYPE = 'PARQUET')


def update_tracking(**context):
    """
    Write job metadata to DynamoDB.
    Airflow reads this for monitoring dashboards.
    """
    metrics = context["ti"].xcom_pull(
        task_ids="start_glue_job", key="job_metrics"
    )
    run_id = context["ti"].xcom_pull(
        task_ids="start_glue_job", key="run_id"
    )

    # In production:
    # import boto3
    # dynamo = boto3.resource('dynamodb')
    # table = dynamo.Table('glue_job_tracking')
    # table.put_item(Item={...})

    logger.info("TRACKING: Saved metrics for run %s", run_id)
    logger.info("TRACKING: Metrics=%s", metrics)


def quarantine_alert(**context):
    """
    Alert when quality gate fails.

    In AWS: SNS notification to Slack/PagerDuty.
    """
    reasons = context["ti"].xcom_pull(
        task_ids="start_glue_job", key="quarantine_reasons"
    )
    logger.error("ALERT: Quality gate failed! Reasons=%s", reasons)

    # In production:
    # import boto3
    # sns = boto3.client('sns')
    # sns.publish(
    #     TopicArn='arn:aws:sns:us-east-1:123456:data-quality-alerts',
    #     Message=f'Glue job quality gate failed. Reasons: {reasons}'
    # )

    logger.error("ALERT: Quality gate failed! Reasons=%s", reasons)


# ============================================================
# DAG
# ============================================================

with DAG(
    dag_id="glue_claims_pipeline",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["glue", "claims", "insurance"],
    doc_md="""
    ## Glue Claims Pipeline
    Orchestrates AWS Glue job for insurance claims processing.
    - Checks source freshness before triggering
    - Runs Glue ETL (extract → validate → quarantine → transform → load)
    - Quality gate: fails if >50% quarantined
    - Loads to Snowflake on pass
    - Alerts team on fail
    """,
) as dag:

    # 1. Check if new data exists
    check_freshness = BranchPythonOperator(
        task_id="check_source_freshness",
        python_callable=check_source_freshness,
    )

    # 2. Skip path
    skip = EmptyOperator(
        task_id="skip_no_new_data",
    )

    # 3. Run Glue job
    run_glue = PythonOperator(
        task_id="start_glue_job",
        python_callable=start_glue_job,
    )

    # 4. Quality gate (branch: pass or fail)
    quality = BranchPythonOperator(
        task_id="quality_gate",
        python_callable=quality_gate,
    )

    # 5a. Load to Snowflake (quality passed)
    load_sf = PythonOperator(
        task_id="load_to_snowflake",
        python_callable=load_to_snowflake,
    )

    # 5b. Quality failed alert
    quality_fail = PythonOperator(
        task_id="quality_failed",
        python_callable=quarantine_alert,
    )

    # 6. Update tracking (runs after either load or alert)
    tracking = PythonOperator(
        task_id="update_tracking",
        python_callable=update_tracking,
        trigger_rule="none_failed_min_one_success",
    )

    # 7. Done
    done = EmptyOperator(
        task_id="done",
        trigger_rule="none_failed_min_one_success",
    )

    # ============================================================
    # DEPENDENCIES
    # ============================================================

    check_freshness >> [run_glue, skip]
    run_glue >> quality >> [load_sf, quality_fail]
    load_sf >> tracking >> done
    quality_fail >> tracking >> done
    skip >> done
