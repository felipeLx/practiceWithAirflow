from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='maintenance_cleanup',
    schedule='@weekly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['maintenance'],
) as dag:

    # Delete logs older than 30 days
    cleanup_logs = BashOperator(
        task_id='cleanup_old_logs',
        bash_command='find $AIRFLOW_HOME/logs -type f -mtime +30 -delete',
    )

    # Cleanup old XCom (via Airflow CLI)
    cleanup_db = BashOperator(
        task_id='cleanup_metadata_db',
        bash_command='airflow db clean --clean-before-timestamp $(date -d "-30 days" +%Y-%m-%d) -y',
    )

    cleanup_logs >> cleanup_db