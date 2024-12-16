import asyncio
from bs4 import BeautifulSoup
import time
import re
from requests import Session
import requests
import time
from requests import Session
from bs4 import BeautifulSoup
'''
This file is to scrape the urls of the houses from the search page 
using Asyncio to speed things up
It adds the files in a items.txt file
'''

async def scrape_list_of_houses(session, url):
    '''
    An async function to scrape a list of urls of induvidual houses from the search page on www.immoweb.be
    '''
    # Set up custom headers
    headers = requests.utils.default_headers()
    headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    })
    # Send GET request
    response = session.get(url, headers=headers)

    # Parse the page content
    soup = BeautifulSoup(response.content, "html.parser")
    await asyncio.sleep(.1)

    # Scrape the property links
    list_url = []

    # Find all the property cards on the page
    for elem in soup.find_all('a', class_="card__title-link"):
        pattern_type = r'/([^/]+)/for-sale'
        match_type = re.search(pattern_type, str(elem))
        type_house = match_type.group(1)
        if type_house == 'apartment' or type_house == 'house':
            list_url.append(elem.get("href"))
            print(elem.get("href"))
            
    # Add the extracted property links to items.txt
    file = open('houses_urls.txt','a')
    for item in list_url:
        file.write(item+"\n")
    file.close()
    return list_url

async def main():
    # The main async function
    n = 1     #start counting at page number n on immoweb url below
    session = Session()
    tasks = [scrape_list_of_houses(session, f"https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isAPublicSale=false&isALifeAnnuitySale=false&page={n + i}&orderBy=relevance") for i in range(5)] #repeat i times
    await asyncio.gather(*tasks)




# Asyncio scrape houses.pyRun the main program and display how long it took to run the program
if __name__ == "__main__":
    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")

