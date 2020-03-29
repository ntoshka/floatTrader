import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


collections = ["Norse Collection","Canals Collection","St. Marc Collection","Blacksite Collection","2018 Inferno Collection","2018 Nuke Collection","Alpha Collection","Assault Collection","Aztec Collection","Baggage Collection","Bank Collection","Cache Collection","Chop Shop Collection","Cobblestone Collection","Dust Collection","Dust 2 Collection","Gods and Monsters Collection","Inferno Collection","Italy Collection","Lake Collection","Militia Collection","Mirage Collection","Nuke Collection","Office Collection","Overpass Collection","Rising Sun Collection","Safehouse Collection","Train Collection","Vertigo Collection"]


def getItemLinks(url):
    

    collectionPage = requests.get(url).content

    soup = BeautifulSoup(collectionPage, 'lxml', from_encoding="utf-8")

    itemSoup = soup.find_all("div", {"class": "col-lg-4 col-md-6 col-widen text-center"})
    itemLinks = [[y["href"] for y in x.find_all("a", href=True) if "https://csgostash.com/skin/" in y["href"]] for x in itemSoup]
    itemLinksFlat = list(set([item for sublist in itemLinks for item in sublist]))

    return itemLinksFlat

def convertRarity(x):
    classes = ["Consumer Grade", "Industrial Grade", "Mil-Spec", "Restricted", "Classified", "Covert", "Knives", "Contraband"]
    for ix, rarity in enumerate(classes):
        if x == rarity:
            return ix 

def getItemInfo(itemUrl):
    itemPage = requests.get(itemUrl).content

    soup = BeautifulSoup(itemPage, 'lxml', from_encoding="utf-8")

    itemName = itemUrl.split("/")[-1]

    rarity = soup.find("a", {"nounderline"}, href=True)["href"].split("/")[-1].replace("+", " ")

    collection = soup.find("p", {"class": "collection-text-label"}).text

    minWear = soup.find("div", {"title": 'Minimum Wear ("Best")'}).text
    maxWear = soup.find("div", {"title": 'Maximum Wear ("Worst")'}).text

    itemTable = soup.find("table").find_all("tr")[1:]

    items = list()

    for row in itemTable:
        cols = row.find_all("td")[:3]
        quality = cols[0].text.replace("\n", "")
        if "Souvenir" in quality:
            continue
        price = cols[1].text.replace("\n", "").replace("€", "")
        listings = cols[2].text.replace("\n", "")

        itemDict = {"itemName": itemName,
                    "quality": quality,
                    "price": price,
                    "rarity": rarity,
                    "rarityNum": convertRarity(rarity),
                    "minWear": minWear,
                    "maxWear": maxWear,
                    "collection": collection,
                    "listings": listings
                    }

        items.append(itemDict)

    return items



startTime = datetime.now()


baseUrl = "https://csgostash.com/collection/"


itemList = list()
for collection in collections:
    url = baseUrl + "The+" + collection.replace(" ", "+")    
    itemLinks = getItemLinks(url)


    for itemUrl in itemLinks:
        itemList = itemList + getItemInfo(itemUrl)

df = pd.DataFrame(itemList)
df["price"] = df["price"].apply(lambda x: x.replace("--", "00").replace(",",".").replace(" ", ""))
df.fillna(-1, inplace=True)

df.to_csv("data/items.csv", index=False)

print(datetime.now() - startTime)
