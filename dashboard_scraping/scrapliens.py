import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv

baseURL = "https://www.linternaute.com/ville/index/villes?page="

dico = {}

# Retrieve desired information, save it in a csv
with open('data/liensvilles.csv', 'w', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['link', 'city'], lineterminator='\n')
    writer.writeheader()

    for pagenum in range(0, 701+1):
        print("Saving information for page # ", pagenum)
        req = requests.get(baseURL + str(pagenum))
        content = req.content
        soup = bs(content, "html.parser")

        all_links = soup.findAll('a')
        for link in all_links:
            if '/ville-' in link['href']:
                dico['link'] = link['href']
                dico['city'] = link.text
                writer.writerow(dico)
