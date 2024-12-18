import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import seaborn as sns

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
    plt.savefig(f"./reports/missing_bar-{date.today()}.png")


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
    plt.savefig(f"./reports/missing_pie-{date.today()}.png") 

def outlier_plots(df):
    outliers = sum(detect_outliers_iqr(df['price']))
    number_of_values = len(df) - df['price'].isna().sum()
    percent_outliers = 100 * outliers / number_of_values
    outlier_analysis=f"Number of outliers detected: {(outliers)}\nOn the number of {number_of_values} values\n{round(percent_outliers, 2)} % outliers \nMean value: € {round(df['price'].mean(),1)}\nMedian value: € {df['price'].median()}\nMode value: € {df['price'].mode()[0]}"
    
    with open(f"./reports/outlier_analysis-{date.today()}.txt","w",encoding='utf8') as file:
        file.write(outlier_analysis)
    
    # Create the plot
    sns.kdeplot(data = df['price'])
    plt.title('Prices of the houses')
    plt.xlim([0,2000000])  
    plt.xlabel("Price (€)")    
    plt.ylabel("Frequency", size=12)                
    plt.grid(True, alpha=0.3, linestyle="--")     
    plt.savefig(f"./reports/prices-{date.today()}.png")

    # Box Plot
    f=sns.boxplot(df['price'])
    f.get_figure().savefig(f"./reports/prices_boxplot-{date.today()}.png")



def main():
    df=pd.read_csv('./data/analysis.csv',index_col=0)
    df = df.drop(columns=["Property ID"])
    missing_plots(df)
    outlier_plots(df)

main()