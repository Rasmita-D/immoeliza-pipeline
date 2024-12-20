import pandas as pd
from datetime import date
def clean_for_analysis():
    df=pd.read_csv(f'./data/houses_data_{date.today()}.csv')
    df=df.drop(['Locality name','Subtype of property','Surface of the plot', 'Garden orientation','Energy class'],axis=1)
    df=df.drop_duplicates(subset=['Property ID'])
    df.to_csv(f'./data/analysis_{date.today()}.csv')

clean_for_analysis()