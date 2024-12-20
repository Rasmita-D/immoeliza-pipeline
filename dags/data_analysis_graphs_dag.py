from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import seaborn as sns
import numpy as np
from pathlib import Path

this_day=date.today()

repo_root = Path(__file__).resolve().parent.parent
data_folder = repo_root / 'data'
reports_folder = repo_root / 'reports'

dag = DAG(                                                     
   dag_id="data_analysis_graphs",                                          
   default_args={
    "email": ["rasmita.damaraju@example.com"],
    "email_on_failure": True
}
)

def detect_outliers_iqr(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (data < lower_bound) | (data > upper_bound)

def missing_plots(df):
    percent_missing = df.isnull().sum() * 100 / len(df)
    percent_non_null = 100 - percent_missing

    plt.figure(figsize=(12, 6))


    # Plot the Non-Missing Values
    bars_non_null = plt.bar(df.columns, percent_non_null, label='Non-Missing Values', 
                            color='#28a745', edgecolor='black', linewidth=1.2)

    # Plot the Missing Values on top of the Non-Missing Values
    bars_missing = plt.bar(df.columns, percent_missing, bottom=percent_non_null, 
                            label='Missing Values', color='#dc3545', edgecolor='black', linewidth=1.2)

    # Customize the plot
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.title('Percentage of Missing and Non-Missing Values per Column', fontsize=16, fontweight='bold')
    plt.ylabel('Percentage (%)', fontsize=14)
    plt.ylim(0, 110)  # Set y-axis limits to provide some space above the bars

    # Add legend outside the plot area
    plt.legend(title='Values', fontsize=12, loc='upper left', bbox_to_anchor=(1, 1))
    plt.savefig(reports_folder/f"missing_bar-{date.today()}.png")
    plt.close()


    # Calculate total number of missing and non-missing values
    total_missing = df.isnull().sum().sum() 
    total_non_missing = df.size - total_missing  


    labels = ['Non-Missing Values', 'Missing Values']
    sizes = [total_non_missing, total_missing]
    colors = ['#28a745', '#dc3545'] 

    # Create the pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, explode=(0.1, 0))  # Explode the first slice for emphasis
    plt.title('Percentage between Missing and Non-Missing Values', fontsize=16)
    plt.savefig(reports_folder/f"missing_pie-{date.today()}.png") 
    plt.close()

def outlier_plots(df):
    outliers = sum(detect_outliers_iqr(df['price']))
    number_of_values = len(df) - df['price'].isna().sum()
    percent_outliers = 100 * outliers / number_of_values
    outlier_analysis=f"Number of outliers detected: {(outliers)}\nOn the number of {number_of_values} values\n{round(percent_outliers, 2)} % outliers \nMean value: € {round(df['price'].mean(),1)}\nMedian value: € {df['price'].median()}\nMode value: € {df['price'].mode()[0]}"

    with open(reports_folder/f"outlier_analysis-{date.today()}.txt","w",encoding='utf8') as file:
        file.write(outlier_analysis)

    # Create the plot
    sns.kdeplot(data = df['price'])
    plt.title('Prices of the houses')
    plt.xlim([0,2000000])  
    plt.xlabel("Price (€)")    
    plt.ylabel("Frequency", size=12)                
    plt.grid(True, alpha=0.3, linestyle="--")     
    plt.savefig(reports_folder/f"prices-{date.today()}.png")
    plt.close()
    
def box_plot(df):    
    # Box Plot
    f = sns.boxplot(x=df['price'])
    f.set_title('Boxplot of house prices (€)')
    plt.savefig(reports_folder/f"prices_boxplot-{date.today()}.png")
    plt.close()

def heatmap(df):
    df_encoded = pd.get_dummies(df, drop_first=True)
    df_encoded = df_encoded.drop(columns=['Open fire'])
    # Select only numeric columns for correlation analysis
    df_numeric = df_encoded.select_dtypes(include=[np.number])

    # Calculate the correlation matrix
    correlation_matrix = df_numeric.corr(method='spearman')

    # Display the correlation matrix
    print(correlation_matrix['price'].sort_values(ascending=False))

    # Create the heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', square=True)
    plt.title('Correlation Heatmap of Property Data')
    plt.savefig(reports_folder/f"corelation_heatmap-{date.today()}.png")
    plt.close()
    
def frequency_construction_year(df):
    # Create the plot
    sns.kdeplot(data = df['Construction year'],bw_adjust=.25)
    plt.title('Construction year')
    plt.xlim([1800,2030])  
    plt.xlabel("Construction year")    
    plt.ylabel("Frequency")                
    plt.grid(True, alpha=0.3, linestyle="--")     
    plt.savefig(reports_folder/f"frequency_construction_year-{date.today()}.png")
    plt.close()
    
def average_price_per_room(df):
    # Drop rows with NaN values in 'rooms' after mapping
    df = df.dropna(subset=['Number of rooms', 'price'])

    # Create the bar plot
    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(x='Number of rooms', y='price', data=df, errorbar=None, palette="viridis")

    # Add value annotations on top of the bars
    for p in bar_plot.patches:
        bar_plot.annotate(f'€{int(p.get_height()):,}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=10)
    def format_price(x, _):
        return f'€{int(x):,}'  # Formats numbers with commas and adds a dollar sign
    # Set labels and title
    plt.xlabel('Number of Rooms', fontsize=12)
    plt.ylabel('Price (€)', fontsize=12)
    plt.title('Average Price by Number of Rooms', fontsize=14)

    # Show the plot
    plt.tight_layout()
    plt.savefig(reports_folder/f"average_price_per_room-{date.today()}.png")
    plt.close()

def average_price_state_building(df):
    # Define the order of categories
    category_order = ['To restore', 'To renovate', 'To be done up', 
                    'Good', 'Just renovated', 'As new']

    # Aggregate data
    df_grouped = df.groupby('State of builing', as_index=False)['price'].mean()

    # Set the style
    sns.set_style("whitegrid")

    # Create the figure
    plt.figure(figsize=(10, 6), dpi=80)

    # Create the bar plot with specified order
    bar_plot = sns.barplot(x='State of builing', y='price', data=df_grouped, 
                palette="viridis", ci=None, order=category_order)
    
    # Add value annotations on top of the bars
    for p in bar_plot.patches:
        bar_plot.annotate(f'€{int(p.get_height()):,}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=10)

    # Customize labels and title
    plt.title('Average Price by State of Building', fontsize=18, fontweight='bold')
    plt.xlabel('State of Building', fontsize=15, fontweight='bold')
    plt.ylabel('Average Price (€)', fontsize=15, fontweight='bold')
    plt.xticks(rotation=90)

    # Add grid
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save and show the plot
    plt.tight_layout()
    plt.savefig(reports_folder/f'average_price_by_state_building-{date.today()}.png', dpi=300)
    plt.close()

def main():
    df=pd.read_csv(data_folder/f'houses_data_{this_day}.csv')
    df=df.drop(['Locality name','Subtype of property','Surface of the plot', 'Garden orientation','Energy class'],axis=1)
    df=df.drop_duplicates(subset=['Property ID'])
    df = df.drop(columns=["Property ID"])
    missing_plots(df)
    outlier_plots(df)
    heatmap(df)
    box_plot(df)
    frequency_construction_year(df)
    average_price_per_room(df)
    average_price_state_building(df)

graphs=PythonOperator(   
    task_id="main",
   python_callable=main,                             
   dag=dag
)

graphs