import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv
from pprint import pprint
import os

def diff(list1, list2):
    """
    Assess difference between 2 lists
    """
    return (list(set(list1).symmetric_difference(set(list2))))

def links_to_scrap():
    """
    Define what is remaining to scrap

    Uses diff function
    """
    if os.path.isfile("data/infos.csv"): # resume scraping
        previously_scrapped = pd.read_csv("data/scrapinfos.csv")
        previously_scrapped_links = previously_scrapped["link"]
        all_cities = pd.read_csv("data/liensvilles.csv")
        all_cities_links = all_cities["link"]
        links_to_scrap = diff(previously_scrapped_links, all_cities_links)
    else: # start scraping for scratch
        links_to_scrap = pd.read_csv("data/liensvilles.csv", nrows=200)
    return links_to_scrap

def create_info_csv(links_to_scrap):
    """
    Create a csv file with all infos for all cities
    """
    with open("data/infos.csv", "a", encoding="utf-8") as csvfile:

        writer = csv.writer(csvfile)

        dicos = []
        dico_keys = []

        # Iterate over each city / link
        for link in links_to_scrap["link"]:

            req = requests.get(link)
            content = req.content
            soup = bs(content, "html.parser")

            dico = {}
            dico["link"] = link
            dico["city"] = links_to_scrap[links_to_scrap["link"]==link]["city"].iloc[0]

            # Get all tables for the city
            tables = soup.findAll('table', class_='odTable odTableAuto')

            # Get all tables for the city
            for i in range(len(tables)):
                all_tr = tables[i].findAll('tr')
                # Get all info for each table
                for tr in all_tr[1:]:
                    k = tr.findAll('td')[0].text # labels
                    v = tr.findAll('td')[1].text # data

                    if "Nom des habitants" in k: # to have identical column names ; city may vary
                        dico["Nom des habitants"] = v
                    elif "Taux de chômage" in k: # to have identical column names ; year may vary
                        dico["Taux de chômage"] = v
                    else:
                        dico[k] = v

                dico_keys = dico.keys()

            dicos.append(dico.values())
            print("Appended information for link" + link)


        writer.writerow(dico_keys)
        writer.writerows(dicos)

if __name__ == "__main__":
    to_scrap = links_to_scrap()
    create_info_csv(to_scrap)
    print("csv created")
