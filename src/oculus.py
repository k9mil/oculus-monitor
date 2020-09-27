import requests
from bs4 import BeautifulSoup


class Content:
    def __init__(self, model, price, url):
        self.model = model
        self.price = price
        self.url = url
    
    def print(self):
        print(f"Model: {self.model} - Price: {self.price} - URL: {self.url}")


class Website:
    def __init__(self, name, url, searchURL, resultListing, resultURL, absoluteURL, modelTag, priceTag):
        self.name = name
        self.url = url
        self.searchURL = searchURL
        self.resultListing = resultListing
        self.resultURL = resultURL
        self.absoluteURL = absoluteURL
        self.modelTag = modelTag
        self.priceTag = priceTag


class Main:
    def __init__(self):
        self.load_data()

    def getPage(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if not response.ok:
            print('Server responded:', response.status_code)
        else:
            return BeautifulSoup(response.text, 'lxml')

    def safeGet(self, pageObj, selector):
        childObj = pageObj.select(selector)
        if childObj is not None and len(childObj) > 0:
            return childObj[0].get_text()
        return ''

    def search(self, model, site):
        bs = self.getPage(site.searchURL + model)
        searchResults = bs.select(site.resultListing)
        for result in searchResults:
            url = result.select(site.resultURL)[0].attrs['href']
            if (site.absoluteURL):
                bs = self.getPage(url)
            else:
                bs = self.getPage(site.url + url)
            if bs is None:
                print("Error.")
                return
            model = self.safeGet(bs, site.modelTag).strip()
            price = self.safeGet(bs, site.priceTag).strip()
            if model != "" and price != "":
                content = Content(model, price, url)
                content.print()
    
    def load_data(self):
        global models
        try:
            try:
                models = open('./data/camera_models.txt').read().split('\n')
            except FileNotFoundError:
                models = open('../data/camera_models.txt').read().split('\n')
        except FileNotFoundError:
            return "File not found!"
            

main = Main()

siteData = [
['OLX', 'https://www.olx.pl/', 'https://www.olx.pl/oferty/q-', 'div.offer-wrapper', 'h3.margintop5 a', 'True', 'h1', 'div.pricelabel']
]

sites = []
for row in siteData:
    sites.append(Website(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

for model in models:
    for targetSite in sites:
        main.search(model, targetSite)