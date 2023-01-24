import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv
from pprint import pprint
import os
import time

def diff(list1, list2):
    """
    Assess difference between 2 lists
    """
    return (list(set(list1).symmetric_difference(set(list2))))

def get_links_to_scrap():
    """
    Define what is remaining to scrap

    Uses diff function to assess differene between already scraped and to-scrap
    """
    if os.path.isfile("data/infos.csv"): # resume scraping
        previously_scrapped = pd.read_csv("data/infos.csv") # Must have a "link" header
        all_links = pd.read_csv("data/liensvilles.csv")
        links_to_scrap = diff(previously_scrapped.iloc[:,0], all_links["link"])
    else: # start scraping for scratch
        all_links = pd.read_csv("data/liensvilles.csv")
        links_to_scrap = all_links["link"]
    return links_to_scrap

# def write_headers(document):
#     with open("data/infos.csv", "a", encoding="utf-8") as csvfile:
#         writer = csv.writer(csvfile)


#     headers = ["link"
#                 #, "city"
#                 ]

#     writer.writerow(headers)


def parse(link):
    req = requests.get(link)
    time.sleep(2)
    if req.status_code == 200:
        with open("data/infos.csv", "a", encoding="utf-8") as csvfile:
            # writer = csv.writer(csvfile)
            content = req.content
            soup = bs(content, "html.parser")

            dico = {}
            dico["link"] = link
            #dico["city"] = all_links[all_links["link"]==link]["city"].iloc[0]

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

            #writer = csv.writer(csvfile)
            colonnes = [dico.keys()]
            writer = csv.DictWriter(csvfile, fieldnames= colonnes, lineterminator='\n')
            # writer.writerow(dico.values())
            writer.writerow(dico)
            print("Wrote information to csv for link " + link)

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
    links_to_scrap = get_links_to_scrap()
    print("# links to scrap: ", len(links_to_scrap))
    with Pool(30) as p:
        p.map(parse, links_to_scrap)
    # print("csv created")
