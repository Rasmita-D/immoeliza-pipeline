from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta, date
import asyncio
from bs4 import BeautifulSoup
import re
from requests import Session
import pandas as pd
from pathlib import Path
import os
import cloudscraper
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

repo_root = Path(__file__).resolve().parent.parent
data_folder = repo_root / 'data'


# Function to scrape URLs
async def scrape_list_of_houses(session, url):
    scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
    },
)
   
    
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        await asyncio.sleep(0.1)

        list_url = []
        for elem in soup.find_all('a', class_="card__title-link"):
            match_type = re.search(r'/([^/]+)/for-sale', str(elem))
            type_house = match_type.group(1) if match_type else None
            if type_house in ['apartment', 'house']:
                list_url.append(elem.get("href"))
        
        today = date.today()
        file_path = data_folder/f"houses_urls_{today}.txt"
        with open(file_path, 'a') as file:
            for item in list_url:
                file.write(item + "\n")
        return list_url
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Wrapper for URL scraping
async def scrape_urls_main():
    base_url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={page}&orderBy=relevance"
    num_pages = 150
    session = Session()
    tasks = [scrape_list_of_houses(session, base_url.format(page=page)) for page in range(1, num_pages + 1)]
    await asyncio.gather(*tasks)

def run_async_scraper():
    asyncio.run(scrape_urls_main())

# Function to read house URLs
def read_house_urls():
    today = date.today()
    file_path = data_folder/f"houses_urls_{today}.txt"
    with open(file_path, "r") as f:
        return [line.strip() for line in f]

# Async function to scrape house details
async def scrape_house(url):
    try:
       
        scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
        },
    )

        response = scraper.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
# Scrapes table content with tag 'th' from the webpage and adds it to a list
        list_keys = []
        for elem in soup.find_all('th', class_="classified-table__header"):
            text = " ".join([str(item) for item in elem.contents])
            text = text.replace("\n", "")
            text = " ".join(text.split())
            list_keys.append(text)  
                     
        # Scrapes table content with tag 'td' from the webpage and adds it to a list
        list_info = []
        for elem in soup.find_all('td', class_="classified-table__data"):
            text = " ".join([str(item) for item in elem.contents])
            text = text.replace("\n", "")
            text = " ".join(text.split())
            list_info.append(text)
                    
        # Create a house_info dictionary and use the 2 lists as key:value pairs
        house_info = {}
        for n in range(len(list_info)):
            house_info[list_keys[n]] = list_info[n]
            
        # Use regex to get the property_id from the url
        pattern = r'/(\d+)$'
        match = re.search(pattern, url)
        property_id = match.group(1)
        
        # Use regex to get the postal code from the url
        pattern_postal_code = r'/(\d{4})/(\d+)$'
        match_postal_code = re.search(pattern_postal_code, url)
        postal_code = match_postal_code.group(1)
        
        # Use regex to get the locality_name from the url
        pattern_locality_name = r'/([^/]+)/(\d{4})/(\d+)$'
        match_locality_name = re.search(pattern_locality_name, url)
        locality_name = match_locality_name.group(1).capitalize()

        # Use regex to get the type_house from the url
        pattern_type = r'/([^/]+)/for-sale'
        match_type = re.search(pattern_type, url)
        type_house = match_type.group(1)

        # Create an empty house dictionary and add the information we need
        house = {}
        house['Property ID'] = property_id
        house['Locality name'] = locality_name
        house['Postal code'] = postal_code

        #Add price to the house dictionary
        try:
            price = house_info['Price'].split()
            for n in price:
                if n[0].isdigit():
                    house['price'] = n
        except:
            house['Price'] = None

        # Add type_house to the house dictionary
        house['Type of property'] = type_house

        # Add Subtype of the house if present on website
        if 'Subtype of property' in house_info:
            house['Subtype of property'] = house_info['Subtype of property']
        else:
            house['Subtype of property'] = None
        
        # Add construction year to the house dictionary
        if 'Construction year' in house_info:
            house['Construction year'] = house_info['Construction year']
        else:
            house['Construction year'] = None
                
        # Add Number of room to the house dictionary if present on website
        if 'Bedrooms' in house_info:
            house['Number of rooms'] = house_info['Bedrooms']
        else:
            house['Number of rooms'] = None

        # Add surface of the plot to the dictionary
        if 'Surface of the plot' in house_info:
            surface_area = house_info['Surface of the plot'].split()[0]
            house['Surface of the plot'] = surface_area
        else:
            house['Surface of the plot'] = None
            
        # Add living area to house dictionary
        if 'Living area' in house_info:
            area = house_info['Living area'].split()[0]
            house['Living area'] = area
        else:
            house['Living area'] = None

         # Add kitchen to the house dictionary. Info is in binary code
        if 'Kitchen type' or 'Kitchen surface' in house_info:
            if 'Kitchen type' in house_info:
                house['kitchen'] = house_info['Kitchen type']
            else:
                if 'Kitchen surface' in house_info:
                    house['kitchen'] = 1
                else:
                    house['kitchen'] = None

        # Add furnished to the house dictionary. Info is in binary code
        if 'Furnished' in house_info:
            if house_info['Furnished'] == 'Yes':
                house['furnished'] = 1
            else:
                house['furnished'] = 0 
        else:
            house['furnished'] = None

        # Add Open fire to the house dictionary. Info is in binary code
        if 'How many fireplaces?' in house_info:
            if house_info['How many fireplaces?'] != 0:
                house['Open fire'] = 1
            else:
                 house['Open fire'] = 0
        else:
            house['Open fire'] = None

        # Add Terrace area to the house dictionary
        if 'Terrace surface' in house_info:
            area = house_info['Terrace surface'].split()[0]
            house['Terrace'] = area
        else:
            house['Terrace'] = None
                
        # Add Garden area to the house dictionary
        if 'Garden surface' in house_info:
            garden = house_info['Garden surface'].split()[0]
            house['Garden'] = garden
        else: 
            house['Garden'] = None 
            
        #Add Garden orientation
        if 'Garden orientation' in house_info:
            house['Garden orientation'] = house_info['Garden orientation']
        else:
            house['Garden orientation'] = None 
            
            # Add number of facades to the house dictionary
        if 'Number of frontages' in house_info:
            house['Number of facades'] = house_info['Number of frontages']
        else:
            house['Number of facades'] = None

        # Add swimming pool to the house dictionary
        if 'Swimming pool' in house_info:
            if house_info['Swimming pool'] == 'Yes':
                house['Swimming pool'] = 1
            else:
                house['Swimming pool'] = 0
        else:
            house['Swimming pool'] = None

        # Add state of building to the house dictionary
        if 'Building condition' in house_info:
            house['State of builing'] = house_info['Building condition']
        else:
            house['State of buiding'] = None
            
        # Add Energy class to the house dictionary
        if 'Energy class' in house_info:
            house['Energy class'] = house_info['Energy class']
        else:
            house['Energy class'] = None
        
        # Add Primary energy consumption to the house dictionary
        if 'Primary energy consumption' in house_info:
            if house_info['Primary energy consumption'] == 'Not specified':
                house['Primary energy consumption'] = None
            else:
                energy_consumption = house_info['Primary energy consumption'].split()
                for n in energy_consumption:
                    if n[0].isdigit():
                        house['Primary energy consumption'] = n            
        else:
            house['Primary energy consumption'] = None
        
        # Add heating type 
        if 'Heating type' in house_info:
            house['Heating type'] = house_info['Heating type'] 
        else:
            house['Heating type'] = None 
        
        # Add Flood zone type to the dictionary
        if 'Flood zone type' in house_info:
            house['Flood zone type'] = house_info['Flood zone type']
        else:
            house['Flood zone type'] = None
        
        # Add double glazing to the dictionary
        if 'Double glazing' in house_info:
            house['Double glazing'] = house_info['Double glazing']
        else:
            house['Double glazing'] = None
        
        # Add cadastral income to the dictionary
        if 'Cadastral income' in house_info:
            cadastral_income = house_info['Cadastral income'].split()
            for n in cadastral_income:
                if n[0].isdigit():
                    house['cadastral_income'] = n
        else:
            house['cadastral_income'] = None
            
        # Add the house to the houses.csv file
        if len(house) != 25:
            print(f"error bij {house['Property ID']}")
        data= []
        data.append(house)
        df = pd.DataFrame(data)
        today = date.today()
        file_path = data_folder/f"houses_data_{today}.csv"
        file_exists = os.path.isfile(file_path)
        df.to_csv(file_path, mode='a', index=False, header=not file_exists)
        
    except:
        print("An exception occurred")

def scrape_houses():
    list_houses = read_house_urls()
    async def main():
        tasks = [scrape_house(url) for url in list_houses]
        await asyncio.gather(*tasks)
    asyncio.run(main())

# Define the DAG
with DAG(
    dag_id='scrape_and_process_houses',
    default_args=default_args,
    description='Scrape house URLs and details using asyncio',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    

    scrape_urls_task = PythonOperator(
        task_id='scrape_urls',
        python_callable=run_async_scraper,
    )

    scrape_houses_task = PythonOperator(
        task_id='scrape_houses',
        python_callable=scrape_houses,
    )

    trigger_target1 = TriggerDagRunOperator(
        task_id='trigger_cleaning',
        trigger_dag_id='data_cleaning_training',
        execution_date='{{ ds }}',
        reset_dag_run=True,
        )
    
    trigger_target2 = TriggerDagRunOperator(
        task_id='trigger_analysis',
        trigger_dag_id='data_analysis_graphs',
        execution_date='{{ ds }}',
        reset_dag_run=True,
    )
    
    scrape_urls_task >> scrape_houses_task >> trigger_target1 >> trigger_target2
    

    

    

