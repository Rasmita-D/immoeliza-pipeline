import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import OneHotEncoder
import joblib
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from pandas.api.types import is_numeric_dtype
from sklearn.model_selection import train_test_split
from datetime import date

def clean_test(df):
    #df=pd.read_csv('./data/sample.csv')
    df=df.drop(['Locality name','Subtype of property','Surface of the plot', 'Garden orientation','Energy class'],axis=1, errors='ignore')
    df=df.drop_duplicates(subset=['Property ID'])
    return df
def check_type_numeric_cols(df):
    '''
    Checks if all numeric columns are really numeric and changes them otherwise.
    It takes and returns a df.
    '''
    all_numeric_columns = ['Property ID', 'Postal code', 'price', 'Construction year',
       'Number of rooms', 'Living area', 'Terrace',
        'Number of facades',
       'Primary energy consumption', 'cadastral_income'] #, 'furnished', , 'Open fire' 'Garden',, 'Swimming pool'
    present_numeric_columns = [item for item in all_numeric_columns if item in df.columns]
    numeric_columns_df =  df[present_numeric_columns]


    # check the selected columns are numeric same as the one specified
    numeric_columns = df.select_dtypes(include=np.number).columns
    is_all_numeric = len(numeric_columns) == len(numeric_columns_df.columns)
    if(not is_all_numeric):
        convert_dict = { }
        for column in numeric_columns_df:
            # Select column contents by column
            try:
                columnSeriesObj = numeric_columns_df[column]
                if is_numeric_dtype(columnSeriesObj.dtype):
                    convert_dict[column] = columnSeriesObj.dtype
                else:
                    convert_dict[column] = np.float64
            except:
                if column == 'price':
                    print(f'{column} not present since it is a prediction')
                continue
        df = df.astype(convert_dict)

    return df


def pre_process_test(df):

    #Assigning a value of 1 whenever a value for the field is present.
    df["Garden"] = np.where(df["Garden"].fillna(0) == 0, 0, 1)
    df["Terrace"] = np.where(df["Terrace"].fillna(0) == 0, 0, 1)
    df["Open fire"] = np.where(df["Open fire"].fillna(0) == 0, 0, 1)
    df["furnished"] = np.where(df["furnished"].fillna(0) == 0, 0, 1)
    df["Swimming pool"] = np.where(df["Swimming pool"].fillna(0) == 0, 0, 1)

    #Condensing features
    df['extra_features']=df["Garden"]+df["Terrace"]+df["Open fire"]+df["furnished"]+df["Swimming pool"]
    df=df.drop(['Garden','Terrace','Open fire','furnished','Swimming pool'],axis=1)

    #Encoding the state of building field
    df['State of builing']=df['State of builing'].fillna('0')
    state_encoder = joblib.load(filename='./utils/state_building_ordinal.pkl')
    df['State of builing']=state_encoder.transform(df[['State of builing']])

    #Replace missing with nan to impute later
    df['State of builing']=df['State of builing'].replace(0.0,np.nan)

    #Encoding kitchen data
    df['kitchen']=df['kitchen'].fillna('0')
    encoder = joblib.load('./utils/kitchen_ordinal.pkl')
    df['kitchen']=encoder.transform(df[['kitchen']])

    #Replace missing with nan to impute later
    df['kitchen']=df['kitchen'].replace(0.0,np.nan)

    df["Flood zone type"] = np.where(df["Flood zone type"].fillna(0) == 'Possible flood zone', 1, 0)
    df['Double glazing'] = np.where(df['Double glazing'].fillna('Yes') == 'Yes', 1, 0)


    with_missing_values=df.columns[df.isna().any()].tolist()

    for l in with_missing_values:
        df[l]=df[l].fillna(df[l].mode().values[0])


    #One hot encoding nominal fields-prop type, sub prop type, locality
    categorical_columns=['Postal code','Type of property','Heating type']
    ohencoder = joblib.load('./utils/one_hot.pkl')
    one_hot_encoded = ohencoder.transform(df[categorical_columns])
    one_hot_df = pd.DataFrame(one_hot_encoded, columns=ohencoder.get_feature_names_out(categorical_columns))

    # Concatenate the one-hot encoded dataframe with the original dataframe
    df = pd.concat([df, one_hot_df.set_axis(df.index)], axis=1)

    # Drop the original categorical columns
    df = df.drop(categorical_columns, axis=1)

    df['Construction year']=date.today().year-df['Construction year']
    #df['construction_year']=2024-df['construction_year']
    return df



