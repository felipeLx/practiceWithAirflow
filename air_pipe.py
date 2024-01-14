from airflow import DAG
# Bash Operator, which you will use to create the two print tasks
from airflow.operators.bash_operator import BashOperator
import datetime as dt

""" 
the owner of the DAG, which is you,
and its start date, in this case July 28, 2021.
The number of times it should keep trying if it is failing: here only once if it does fail,
and the ‘retry delay’, or the time to wait between subsequent tries,
which in this case is five minutes.
"""
default_args = {
    'owner': 'me',
    'start_date': dt.datetime(2021, 7, 28),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

#  used for instantiating your workflow as a DAG object.
"""
name of your DAG, 'simple example';
a description for your workflow,
the default arguments to apply to your DAG, which
scheduling instructions.
"""
dag = DAG('simples_example',
          description = 'A simple example DAG',
          default_args = default_args,
          schedule_interval = dt.timedelta(seconds=5))


# tasks definitions
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

# dependencies for your workflow
task1 >> task2
"""
the double 'greater than' notation
specifies that task two is downstream from task one.
This means that task one, which we named 'print hello', will run first.
Once 'print hello' runs successfully, task two, or 'print date', will run.
"""
