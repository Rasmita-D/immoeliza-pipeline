import streamlit as st
import pandas as pd
import requests
import json
from PIL import Image
from requests.models import Response

def underscore_col_name(column):
   return column.replace(" ", "_")
# Path to the JSON file
json_file = "./streamlit/data_column_details.json"  # Replace with your JSON file path

# Load the JSON data
with open(json_file, "r") as file:
    data = json.load(file)

# Accessing the data
all_columns = data["all_columns"]
numerical_columns = data["numerical_columns"]
non_numerical_columns = data["non_numerical_columns"]
unique_values = data["unique_values"]
all_columns.remove('price')
numerical_columns.remove('price')
num_col_dict = {underscore_col_name(col): 0 for col in numerical_columns}

# Create a dictionary for non-numerical columns with "" as values
non_num_col_dict = {underscore_col_name(col): "" for col in non_numerical_columns}

# Merge the two dictionaries
property = {**num_col_dict, **non_num_col_dict}


#st.set_page_config(layout="wide")
st.set_page_config(
    page_title="'Immo Eliza Property Price Predictor",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

image, title = st.columns([0.8,2])
with image:
  image = Image.open('./streamlit/property.png')
  st.image(image, width=200)
with title:
  st.title(':rainbow[Immo Eliza Property Price Predictor]')

  st.subheader("Provide the property details to predict the price")
number_of_columns = data["number_of_columns"]
data_per_col = int(number_of_columns / 3)
col1, col2, col3 = st.columns(3)

with col1:
    columns = all_columns[:data_per_col]
    for col in columns:
        if col in numerical_columns:
            property[underscore_col_name(col)] = st.number_input(f":blue[What is the value of {col}?]", min_value=0, max_value=9999,step=2)
        if col in non_numerical_columns:
            options = tuple(unique_values.get(col,['']))
            property[underscore_col_name(col)] = st.selectbox(f":blue[what is the {col}?]", options)

with col2:
    columns = all_columns[data_per_col:data_per_col*2]
    for col in columns:
        if col in numerical_columns:
            property[underscore_col_name(col)] = st.number_input(f":blue[What is the value of {col}?]", min_value=0, max_value=9999,step=2)
        if col in non_numerical_columns:
            options = tuple(unique_values.get(col,['']))
            property[underscore_col_name(col)] = st.selectbox(f":blue[what is the {col}?]", options)

with col3:
    columns = all_columns[data_per_col*2:number_of_columns]
    for col in columns:
        if col in numerical_columns:
            property[underscore_col_name(col)] = st.number_input(f":blue[What is the value of {col}?]", min_value=0, max_value=9999,step=2)
        if col in non_numerical_columns:
            options = tuple(unique_values.get(col,['']))
            property[underscore_col_name(col)] = st.selectbox(f":blue[what is the {col}?]", options)


json_data = json.dumps(property)
#base_url = 'https://immoeliza-pipeline-57k8.onrender.com/'
base_url = 'http://127.0.0.1:8000'
endpoint = 'property_info'
c0l1,col2,col3 = st.columns([10,2,10])
col11,col21,col31 = st.columns([0.5,1,0.3])
result = Response()

with col2:
  st.markdown("""
<style>.element-container:has(#button-after) + div button {
 background-color: blue;
 p{
 color : white;
  }
 }</style>""", unsafe_allow_html=True)
  st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
  #st.button('My Button')
  if st.button('Predict Price'):
      response = requests.get(base_url)
      if response.status_code == 200:
          #st.success(response.content)
        
        result = requests.post(url=f'{base_url}/{endpoint}', data=json_data)
        with col21:
          if result.status_code == 200:
            st.balloons()
            #st.success(f"### Predicted price for your property is € {result.json()['price']}")
            st.success(f"### Predicted price for your property is € {result.json()}")

          else:
            st.error(f"{result.content}")