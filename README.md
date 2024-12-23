## :classical_building: Description

This project explores using airflow to automate the scraping, analysis and preprocessing of house data to create a machine learning model that predicts house prices.

API: https://immoeliza-pipeline-57k8.onrender.com/

Web App: https://rasmita-d-immoeliza-pipeline-streamlitstream-lit-wylbfl.streamlit.app/

##	:building_construction: Repo Structure
```
.
├── README.md
├── api
│   ├── Dockerfile
│   ├── app.py
│   ├── predict.py
│   ├── preprocess.py
│   ├── requirements.txt
│   └── utils
│   │   ├── kitchen_ordinal.pkl
│   │   ├── one_hot.pkl
│   │   ├── state_building_ordinal.pkl
│   │   └── xgboost-{date}.pkl
├── streamlit
│   ├── property.png
│   ├── data_column_details.json
│   └── stream_lit.py
├── dags
│   ├── api.py
│   ├── data_analysis_graphs_dag.py
│   ├── data_cleaning_training_dag.py
│   ├── house_data_scraping_dag.py
│   └── training_models.py
├── data
│   ├── houses_data_{date}.csv
│   ├── houses_urls_{date}.txt
│   ├── test-{date}.csv
│   └── train-{date}.csv
├── reports
│   ├── average_price_by_state_building-{date}.png
│   ├── average_price_per_room-{date}.png
│   ├── corelation_heatmap-{date}.png
│   ├── frequency_construction_year-{date}.png
│   ├── missing_bar-{date}.png
│   ├── missing_pie-{date}.png
│   ├── outlier_analysis-{date}.txt
│   ├── prices-{date}.png
│   └── prices_boxplot-{date}.png
├── scripts
│   ├── analysis_dashboard.py
│   ├── api.py
│   ├── data_cleaning_analysis.py
│   ├── data_cleaning_training.py
│   ├── data_scraping.py
│   ├── training_models.py
│   └── web_ui.py
├── utils
│   ├── kitchen_ordinal.pkl
│   ├── one_hot.pkl
│   ├── state_building_ordinal.pkl
│   └── xgboost-{date}.pkl
├── requirements.txt
└── README.md
```

## 	:gear: Our Pipeline
![image](https://github.com/user-attachments/assets/f1e64bd0-00a3-43f1-9bd8-8589f4d6aaf3)

## 🛎️ How to use?

1. Clone the repo.
2. In your airflow virtual environment, install the requirements.
3. Run the airflow scheduler, the pipeline to scheduled to run at 2 am daily.
4. You can manually kick off the automation by running the DAG 'scrape_and_process_houses'.

## Sample from Airflow
![Screenshot 2024-12-23 100352](https://github.com/user-attachments/assets/2121237f-0091-45e8-a8fa-8c1c37c0386c)


## :chart_with_upwards_trend: Enhancements
1. Train the model on the data scraped from the last 2 weeks instead of the last day.
2. Build dashboard for the reports generated in streamlit.
3. Push data files into the git repo.


## ⏱️ Timeline

This project took five days for completion.

## 📌 Personal Situation
This project was done as part of the AI Boocamp at BeCode.org. 


