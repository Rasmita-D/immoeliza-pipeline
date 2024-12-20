import pandas as pd
from datetime import date
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

repo_root = Path(__file__).resolve().parent.parent
data_folder = repo_root / 'data'

def clean_for_analysis():
    df=pd.read_csv(data_folder/f"houses_data_{date.today()}.csv")
    df=df.drop(['Locality name','Subtype of property','Surface of the plot', 'Garden orientation','Energy class'],axis=1)
    df=df.drop_duplicates(subset=['Property ID'])
    df.to_csv(data_folder/f'/analysis_{date.today()}.csv')

dag = DAG(                                                     
   dag_id="data_cleaning_analysis",                                          
   default_args={
    "email": ["rasmita.damaraju@example.com"],
    "email_on_failure": True
}
)

data_cleaning_task = PythonOperator(
        task_id='scrape_urls',
        python_callable=clean_for_analysis,
        dag=dag
    )

data_cleaning_task