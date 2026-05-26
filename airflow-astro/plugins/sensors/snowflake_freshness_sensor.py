# plugins/sensors/snowflake_freshness_sensor.py
from airflow.sensors.base import BaseSensorOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

class SnowflakeFreshnessSensor(BaseSensorOperator):
    """Wait until Snowflake table has fresh data before proceeding."""
    
    def __init__(self, table, max_age_hours=24, snowflake_conn_id='snowflake_default', **kwargs):
        super().__init__(**kwargs)
        self.table = table
        self.max_age_hours = max_age_hours
        self.snowflake_conn_id = snowflake_conn_id

    def poke(self, context):
        hook = SnowflakeHook(snowflake_conn_id=self.snowflake_conn_id)
        result = hook.get_first(f"""
            SELECT TIMESTAMPDIFF('hour', MAX(loaded_at), CURRENT_TIMESTAMP()) 
            FROM {self.table}
        """)
        age_hours = result[0]
        self.log.info(f"Table {self.table} last updated {age_hours} hours ago")
        return age_hours <= self.max_age_hours