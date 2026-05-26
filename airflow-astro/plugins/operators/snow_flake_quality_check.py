# plugins/operators/snowflake_quality_check.py
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.models import BaseOperator

class SnowflakeDataQualityOperator(BaseOperator):
    """
    Reusable operator: runs quality checks on Snowflake tables.
    Business units just call it — don't need to write SQL.
    """
    def __init__(self, table, checks, snowflake_conn_id='snowflake_default', **kwargs):
        super().__init__(**kwargs)
        self.table = table
        self.checks = checks
        self.snowflake_conn_id = snowflake_conn_id

    def execute(self, context):
        from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
        hook = SnowflakeHook(snowflake_conn_id=self.snowflake_conn_id)

        for check_name, check_sql in self.checks.items():
            result = hook.get_first(check_sql)
            if result[0] > 0:
                raise ValueError(f"Quality check '{check_name}' failed: {result[0]} bad rows in {self.table}")
            self.log.info(f"Quality check '{check_name}' passed for {self.table}")