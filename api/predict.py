import sys

import preprocess
import numpy as np
import pandas as pd

import joblib
from datetime import date


this_day=date.today()

def test(raw_df):
    clean_df = preprocess.clean_test(raw_df)
    #n_df = preprocess.check_type_numeric_cols(clean_df)
    target = ['price']
    if target[0] in clean_df.columns:
        clean_df = clean_df.drop(target, axis =1)
    df_processed = preprocess.pre_process_test(clean_df)

    
    df_ml = df_processed
    target = 'price'
    if target in df_ml.columns:
        
        #features = list(set(df_ml.columns) - set(target))
        X_test = np.array(df_ml.drop(columns=[target]))
    else:
        X_test = np.array(df_ml)


    # Standardizing each feature using the train mean and standard deviation
    if 0:
        # Get mean and standard deviation from training set (per feature)
        idx=0

        mean = np.mean(X_test[:,idx])
        stdev = np.std(X_test[:,idx])

        X_test[:,idx] = (X_test[:,idx] - mean)/stdev
  

    regressor = joblib.load('utils/xgboost-{this_day}.pkl')
    
    #print(f'\nPredicted price for your property is:{regressor.predict(X_test)}\n')
    #raw_df['price'] = regressor.predict(X_test)
    predictions = regressor.predict(X_test)
    predict_prices = predictions.tolist()
    return predict_prices[0]
'''
if __name__ == '__main__':
    input_string = "20394069,Tienen,3300,184000,apartment,,1972,2,,81,1,,,22,,,4,,To renovate,C,202,Gas,Non flood zone,Yes,755"
    #input("Enter comma-separated values: ")
    values = input_string.split(',')
    important_columns = ['Property ID','Locality name','Postal code','price','Type of property','Subtype of property','Construction year','Number of rooms','Surface of the plot','Living area','kitchen','furnished','Open fire','Terrace','Garden','Garden orientation','Number of facades','Swimming pool','State of builing','Energy class','Primary energy consumption','Heating type','Flood zone type','Double glazing','cadastral_income']     
    if len(values) != len(important_columns):
        raise ValueError(f"Expected {len(important_columns)} values, but got {len(values)}")
    raw_df = pd.DataFrame([values], columns=important_columns)
    #raw_df = pd.read_csv('./data/sample.csv')
    test(raw_df)

if __name__ == '__main__':
    
    data1 = {'Property_ID': 20394069, 'Locality_name': 'Tienen', 'Postal_code': 3300, 'price':3350, 'Type_of_property': 'apartment', 'Subtype_of_property': 'string', 'Construction_year': 1972, 'Number_of_rooms': 2, 'Surface_of_the_plot': 10, 'Living_area': 120, 'kitchen': 'Installed', 'furnished': 0, 'Open_fire': 0, 'Terrace': 0, 'Garden': 0, 'Garden_orientation': 'string', 'Number_of_facades': 0, 'Swimming_pool': 0, 'State_of_builing': 'Good', 'Energy_class': 'string', 'Primary_energy_consumption': 0, 'Heating_type': 'string', 'Flood_zone_type': 'Non flood zone', 'Double_glazing': 'yes', 'cadastral_income': 755}
    df = pd.DataFrame([data1])
    old_colnames = df.columns
    column_names = ['Property ID', 'Locality name', 'Postal code', 'price',
       'Type of property', 'Subtype of property', 'Construction year',
       'Number of rooms', 'Surface of the plot', 'Living area', 'kitchen',
       'furnished', 'Open fire', 'Terrace', 'Garden', 'Garden orientation',
       'Number of facades', 'Swimming pool', 'State of builing',
       'Energy class', 'Primary energy consumption', 'Heating type',
       'Flood zone type', 'Double glazing', 'cadastral_income']
    df = df.rename(columns=dict(zip(old_colnames, column_names)))
    

    df = pd.read_csv('../Data/sample.csv')
    df_single_row = df.loc[[1]]
    print(df_single_row)
   
    print(test(df))
'''