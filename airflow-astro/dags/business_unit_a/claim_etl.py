# dags/business_unit_a/claims_etl.py
from factories.etl_dag_factory import create_etl_dag

claims_dag = create_etl_dag(
    dag_id='bu_a_claims_etl',
    source_table='RAW.external_claims',
    target_table='MARTS.fct_claims',
    transform_sql="INSERT INTO MARTS.fct_claims SELECT ... FROM RAW.external_claims",
)