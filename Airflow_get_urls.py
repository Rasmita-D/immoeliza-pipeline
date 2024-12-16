from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define scrape task logic
def scrape_task():
    script_path = "C:\\Users\\nicol\\GitHub Repo's\\immoeliza-pipeline\\Asyncio get urls.py"
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Scraping failed: {result.stderr}")


# Define DAG
with DAG(
    dag_id='scrape_houses_dag',
    default_args=default_args,
    description='Scrape Immoweb URLs every night',
    schedule='0 2 * * *',  # Runs daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Define task
    scrape_houses = PythonOperator(
        task_id='scrape_houses_task',
        python_callable=scrape_task,
    )

    scrape_houses
