"""This DAG has the goal to simulate a ML Training pipeline
Follow the instruction in the README.md to complete the DAG.
"""
from collections import _T1
from datetime import timedelta

from airflow import DAG
from airflow.hooks.sqlite_hook import SqliteHook
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

from src.model_toolbox import preprocess_raw_data, fit_model, predict

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

    t2 = BashOperator(
        task_id='sleep',
        bash_command='sleep 5',
        retries=3,
        dag=dag)

    templated_command = """
        {% for i in range(5) %}
            echo "{{ ds }}"
            echo "{{ macros.ds_add(ds, 7)}}"
            echo "{{ params.my_param }}"
        {% endfor %}
    """

    t3 = BashOperator(
        task_id='templated',
        bash_command=templated_command,
        params={'my_param': 'Parameter I passed in'},
        dag=dag)

    t2.set_upstream(t1)
    t3.set_upstream(t1)