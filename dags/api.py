from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
from datetime import date
from pathlib import Path

this_day=date.today()
repo_root = Path(__file__).resolve().parent.parent
api_folder= repo_root / 'api'

# GitHub repository details
REPO_URL = 'https://github.com/Rasmita-D/immoeliza-pipeline.git'
BRANCH = 'api_model_push_dedicated'
REPO = 'immoeliza-pipeline'
SOURCE_FILE = api_folder/'xgboost.pkl'
TARGET_FILE = 'api/xgboost.pkl'  # File to replace the target file
GITHUB_TOKEN = "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" 
#"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"  # Hardcoded GitHub token
GIT_USER_NAME = "adheeba"
GIT_USER_EMAIL = "adeebathahsin@gmail.com"

# DAG definition
with DAG(
    dag_id='replace_file_in_github_repo',
    description='Replace one file with another in a GitHub repo using Airflow',
    schedule_interval=None,  # Manual run
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Clone the GitHub repository
    clone_repo = BashOperator(
        task_id='clone_repo',
        bash_command=(
            f'git clone https://{GITHUB_TOKEN}@{REPO_URL.replace("https://", "")} repo_dir && '
            f'cd repo_dir && git checkout {BRANCH} && '
            f'git config user.name "{GIT_USER_NAME}" && '
            f'git config user.email "{GIT_USER_EMAIL}" &&'
            f'cp {SOURCE_FILE} {TARGET_FILE} &&'
            f'git add {TARGET_FILE} && '
            f'git commit -m "Replaced xgboost model via Airflow for the date: {this_day}" && '
            f'git push https://{GITHUB_TOKEN}@{REPO_URL.replace("https://", "")} {BRANCH}'
        ),
    )
    
    ''' 
    # Task 2: Replace the target file with the source file
    replace_file = BashOperator(
        task_id='replace_file',
        bash_command=(
            f'cp $AIRFLOW_HOME/{SOURCE_FILE} repo_dir/{TARGET_FILE}'
        ),
    )
    # Task 3: Commit and push the changes&&&&&&&&&&
    commit_and_push = BashOperator(
        task_id='commit_and_push',
        bash_command=(
            'cd repo_dir/{REPO} && '
            'git add {TARGET_FILE} && '
            'git commit -m "Replaced target file with source file via Airflow" && '
            f'git push https://{GITHUB_TOKEN}@{REPO_URL.replace("https://", "")} {BRANCH}'
        ),
    )
    '''
    # Define task dependencies
    clone_repo

