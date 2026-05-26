# dags/factories/etl_dag_factory.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from operators.snow_flake_quality_check import SnowflakeDataQualityOperator
from datetime import datetime, timedelta

def create_etl_dag(dag_id, source_table, target_table, transform_sql, schedule='@daily'):
    """
    Factory: business units create DAGs by calling this function.
    No Airflow knowledge needed — just provide table names + SQL.
    """
    default_args = {
        'owner': 'data_platform',
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule=schedule,
        start_date=datetime(2024, 1, 1),
        catchup=False,
    )

    with dag:
        extract = SQLExecuteQueryOperator(
            task_id='extract_load',
            sql=f"INSERT INTO {target_table}_staging SELECT * FROM {source_table}",
            conn_id='snowflake_default',
        )

        transform = SQLExecuteQueryOperator(
            task_id='transform',
            sql=transform_sql,
            conn_id='snowflake_default',
        )

        quality = SnowflakeDataQualityOperator(
            task_id='quality_check',
            table=target_table,
            checks={'row_count': f"SELECT CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END FROM {target_table}"},
        )

        extract >> transform >> quality

    return dag