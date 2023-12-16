from airflow import DAG
from airflow.operators.bash_operator import BashOperator
import datetime as dt

default_args = {
    'owner': 'me',
    'start_date': dt.datetime(2021, 7, 28),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

dag = DAG('simples_example',
          description = 'A simple example DAG',
          default_args = default_args,
          schedule_interval = dt.timedelta(seconds=5))

task1 = BashOperator(
    task_id = 'print_hello',
    bash_command = 'echo \'Grettings. The date and time are \'',
    dag = dag,
)

task2 = BashOperator(
    task_id = 'print_date',
    bash_command = 'date',
    dag = dag,
)

task1 >> task2
