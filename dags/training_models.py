import numpy as np
from sklearn.model_selection import train_test_split
import joblib
from xgboost.sklearn import XGBRegressor
from sklearn.metrics import mean_squared_error
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow import DAG
#from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from datetime import date
from pathlib import Path

this_day=date.today()
repo_root = Path(__file__).resolve().parent.parent
data_folder = repo_root / 'data'
utils_folder= repo_root / 'utils'
api_folder= repo_root / 'api'
train_data_path = data_folder/f'train-{this_day}.csv'
test_data_path = data_folder/f'test-{this_day}.csv'
model_path = utils_folder/f'xgboost-{this_day}.pkl'
api_model_path = api_folder/'xgboost.pkl'
import pandas as pd


import shutil

def copy_model_to_api():
    
    # Define the location of your GitHub repository (make sure the directory is initialized as a Git repository)
    repo_path = "../Projects/immo-eliza-deployment/api/"
    
    # Copy the trained model to the repository folder
    shutil.copy(model_path, repo_path)
    
    print(f"Model updated at: {repo_path}")

def train():
    '''
    load a df with the training data
    '''
    try:
        df_train = pd.read_csv(train_data_path)
        print(f"INFO: The file read from {train_data_path} for training.")
    except FileNotFoundError:
        print(f"Error: The file at {train_data_path} was not found.")
        exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit()

    if df_train is None:
        print("could not load training data")
        exit()

    '''
    load a df with the testing data
    '''
    try:
        df_test = pd.read_csv(test_data_path)
        print(f"INFO: The file read from {test_data_path} for testing.")
    except FileNotFoundError:
        print(f"Error: The file at {test_data_path} was not found.")
        exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit()

    if df_test is None:
        print("could not load test data")
        exit()

    target = ['price']
    unwanted_string = 'Unnamed: 0'
    unwanted = [unwanted_string]
    if unwanted_string in df_train.columns:
        df_train = df_train.drop(unwanted, axis=1)
    if unwanted_string in df_test.columns:
        df_test = df_test.drop(unwanted, axis=1)
    features = list(set(df_train.columns) - set(target))
    

    X_train = np.array(df_train.drop(columns=target))
    y_train = np.array(df_train.drop(columns=features))
    X_test = np.array(df_test.drop(columns=target))
    y_test = np.array(df_test.drop(columns=features))

    #X_train, X_test, y_train, y_test = train_test_split(X,y, random_state=41, test_size=0.2)

    # Standardizing each feature using the train mean and standard deviation
    if 0:
        # Get mean and standard deviation from training set (per feature)
        idx=0

        mean = np.mean(X_train[:,idx])
        stdev = np.std(X_train[:,idx])

        X_train[:,idx] = (X_train[:,idx] - mean)/stdev

        # Get mean and standard deviation from testing set (per feature)
        mean = np.mean(X_test[:,idx])
        stdev = np.std(X_test[:,idx])

        # Standardize training and testing set using the mean and standard deviation from the training set

        X_test[:,idx] = (X_test[:,idx] - mean)/stdev
  

    #regressor = XGBRegressor(random_state=41, max_depth=5, min_child_weight=3)

    #initialize the regressor
    regressor = XGBRegressor(
    objective='reg:squarederror',  # Use square error for regression
    n_estimators=100,              # Number of boosting rounds
    learning_rate=0.2,             # Learning rate
    max_depth=3,
    min_child_weight=3,                  # Maximum depth of a tree
    random_state=42
    )
    '''
    from sklearn.model_selection import GridSearchCV
    param1 = {
    'max_depth':range(3,10,2),
    'min_child_weight':range(1,6,2)
    }
    clf = GridSearchCV(
    estimator=regressor,
    param_grid=param1,
    cv=5,
    n_jobs=5,
    verbose=1
    )
    clf.fit(X_train, y_train)
    print(clf.best_params_)
    '''
    regressor.fit(X_train, y_train)
    score = regressor.score(X_train, y_train)
    print(f'Training score for the model is {score}')

    score = regressor.score(X_test, y_test)
    print(f'Testing score for the model is {score}')

    y_pred = regressor.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print(f'MSE:{mse}')
    print(f'RMSE:{rmse}')

    # Calculate the mean and standard deviation of the target values
    mean_y_true = np.mean(y_test)
    std_y_true = np.std(y_test)

    # Calculate RMSE as a percentage of the target's mean and standard deviation
    rmse_mean_percentage = (rmse / mean_y_true) * 100
    rmse_std_percentage = (rmse / std_y_true) * 100
    print(f"RMSE as % of Mean: {rmse_mean_percentage:.2f}%")
    print(f"RMSE as % of Std Dev: {rmse_std_percentage:.2f}%")

#saving model to utils folder
    try:
        joblib.dump(regressor, model_path)
        print(f'Model is stored at {model_path}')
    except FileNotFoundError:
        print(f"Error: Couldn't save model: The folder to save file {model_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

#saving model to api folder for api rendering automation
    
    try:
        joblib.dump(regressor, api_model_path)
        print(f'Model is also stored at {api_model_path}')
    except FileNotFoundError:
        print(f"Error: Couldn't save model: The folder to save file {api_model_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

with DAG(dag_id="training_models_dag",
         catchup=False) as dag:
    
    task1 = PythonOperator(
        task_id="training_xgboost",
        python_callable=train)
    '''
    task2 = PythonOperator(
        task_id="copying_model",
        python_callable=copy_model_to_api)
    '''
    trigger_target = TriggerDagRunOperator(
        task_id='trigger_repo_push',
        trigger_dag_id='replace_file_in_github_repo',
        execution_date='{{ ds }}',
        reset_dag_run=True
    )

task1 >> trigger_target
