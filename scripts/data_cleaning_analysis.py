import pandas as pd

def clean_for_analysis():
    df=pd.read_csv('./data/sample.csv')
    df=df.drop(['Locality name','Subtype of property','Surface of the plot', 'Garden orientation','Energy class'],axis=1)
    df=df.drop_duplicates(subset=['Property ID'])
    df.to_csv('./data/analysis.csv')

clean_for_analysis()