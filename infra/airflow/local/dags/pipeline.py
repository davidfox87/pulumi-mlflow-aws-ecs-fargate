"""This DAG has the goal to simulate a ML Training pipeline
Follow the instruction in the README.md to complete the DAG.
"""

from datetime import timedelta

from airflow import DAG
from airflow.hooks.sqlite_hook import SqliteHook
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# default_args when passed to a DAG, it will apply to any of its operators
default_args = {
                "start_date": "2022-8-29",
                "email": ["foxy1987@gmail.com"],
                "email_on_failure": False,
                "email_on_retry": False,
                "retries": 2,
                "retry_delay": timedelta(minutes=5)
                }


dag = DAG("training_pipeline",
          description="ML Training Pipeline",
          # train every first day of the month
          #schedule_interval="@monthly",
          schedule_interval='* * * * *',
          default_args=default_args,
          dagrun_timeout=timedelta(minutes=60*10),
          catchup=False
    )

with dag:
    
    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id='print_date',
        bash_command='date',
        dag=dag)

    # invoke_lambda_function = AwsLambdaInvokeFunctionOperator(
    #     task_id='setup__invoke_lambda_function',
    #     function_name="testLambda-2a895f6",
    #     payload=SAMPLE_EVENT,
    # )

    t1
    #t3.set_upstream(t1)