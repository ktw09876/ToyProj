from airflow import DAG
from airflow.operators import PythonOperator
from datetime import datetime
import os


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
}

dag = DAG(
    'covid_s3_upload_dag',
    default_args=default_args,
    schedule_interval=None,  
)


def run_script():
    script_path = "/path/to/your/script.py"  
    os.system(f"wsl python {script_path}")


run_script_task = PythonOperator(
    task_id='run_script',
    python_callable=run_script,
    dag=dag,
)
