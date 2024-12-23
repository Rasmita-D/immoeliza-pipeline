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

def clean_initial():
    df=pd.read_csv('./data/sample.csv')
    df=df.drop(['Locality name','Subtype of property','Surface of the plot', 'Garden orientation','Energy class'],axis=1)
    df=df.drop_duplicates(subset=['Property ID'])
    return df

def pre_process_train(df,price):
    df['price']=price
    #Assigning a value of 1 whenever a value for the field is present.
    df["Garden"] = np.where(df["Garden"].fillna(0) == 0, 0, 1)
    df["Terrace"] = np.where(df["Terrace"].fillna(0) == 0, 0, 1)
    df["Open fire"] = np.where(df["Open fire"].fillna(0) == 0, 0, 1)
    df["furnished"] = np.where(df["furnished"].fillna(0) == 0, 0, 1)
    df["Swimming pool"] = np.where(df["Swimming pool"].fillna(0) == 0, 0, 1)

    #Condensing features
    df['extra_features']=df["Garden"]+df["Terrace"]+df["Open fire"]+df["furnished"]+df["Swimming pool"]
    df=df.drop(['Garden','Terrace','Open fire','furnished','Swimming pool'],axis=1)

    #dropping null price values
    df=df.dropna(subset=['price'])

    #Encoding the state of building field
    df['State of builing']=df['State of builing'].fillna('0')
    state_encoder = OrdinalEncoder(categories=[['0','To restore','To renovate','To be done up','Good','Just renovated','As new']])
    df['State of builing']=state_encoder.fit_transform(df[['State of builing']])
    joblib.dump(state_encoder,'./utils/state_building_ordinal.pkl')
    #Replace missing with nan to impute later
    df['State of builing']=df['State of builing'].replace(0.0,np.nan)

    #Encoding kitchen data
    df['kitchen']=df['kitchen'].fillna('0')
    encoder = OrdinalEncoder(categories=[['0','Not installed','1','Installed','Semi equipped','Hyper equipped']])
    df['kitchen']=encoder.fit_transform(df[['kitchen']])
    joblib.dump(encoder,'./utils/kitchen_ordinal.pkl')
    #Replace missing with nan to impute later
    df['kitchen']=df['kitchen'].replace(0.0,np.nan)

    df["Flood zone type"] = np.where(df["Flood zone type"].fillna(0) == 'Possible flood zone', 1, 0)
    df['Double glazing'] = np.where(df['Double glazing'].fillna('Yes') == 'Yes', 1, 0)


    with_missing_values=df.columns[df.isna().any()].tolist()
    missing_numeric=[]
    for l in with_missing_values:
        if is_numeric_dtype(df[l]):
            missing_numeric.append(l)
        else:
            df[l]=df[l].fillna(df[l].mode().values[0])

    missing_numeric.insert(0,'price')
    to_impute=df[missing_numeric]

    imputer = IterativeImputer(max_iter=10, random_state=0)
    imputed = imputer.fit_transform(to_impute)
    test=pd.DataFrame(imputed,columns=to_impute.columns)

    for l in missing_numeric:
        df[l]=test[l].to_numpy()

    #One hot encoding nominal fields-prop type, sub prop type, locality
    categorical_columns=['Postal code','Type of property','Heating type']
    ohencoder = OneHotEncoder(drop='first',sparse_output=False,handle_unknown='ignore')
    one_hot_encoded = ohencoder.fit_transform(df[categorical_columns])
    joblib.dump(ohencoder,'./utils/one_hot.pkl')
    one_hot_df = pd.DataFrame(one_hot_encoded, columns=ohencoder.get_feature_names_out(categorical_columns))

    # Concatenate the one-hot encoded dataframe with the original dataframe
    df = pd.concat([df, one_hot_df.set_axis(df.index)], axis=1)

    # Drop the original categorical columns
    df = df.drop(categorical_columns, axis=1)
    df['Construction year']=date.today().year-df['Construction year']
    df = df.drop(['price'], axis=1)
    
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
    
    return df

def main():
    df=clean_initial()
    y=df['price']
    X=df.drop(['price'],axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X,y, random_state=10, test_size=0.2)
    X_train=pre_process_train(X_train,y_train)
    X_test=pre_process_test(X_test)
    return X_train, X_test, y_train, y_test

X_train, X_test, y_train, y_test=main()
X_train['price']=y_train
X_test['price']=y_test
X_train.to_csv('./data/train.csv')
X_test.to_csv('./data/test.csv')


