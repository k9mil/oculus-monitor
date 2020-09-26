import requests
from bs4 import BeautifulSoup


class Content:
    def __init__(self, model, price, url):
        self.model = model
        self.price = price
        self.url = url
    
    def print(self):
        print(f"Model: {self.model} - Price: {self.price}")


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
    def getPage(self, url):
        response = requests.get(url)
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
            model = self.safeGet(bs, site.modelTag)
            price = self.safeGet(bs, site.priceTag)
            if model != "" and price != "":
                content = Content(model, price, url)
                content.print()

main = Main()

siteData = [
['OLX', 'https://www.olx.pl/', 'https://www.olx.pl/oferty/q-', 'div.offer-wrapper', 'h3.margintop5 a', 'True', 'h1', 'div.pricelabel'],
['Allegro', 'https://allegro.pl/', 'https://allegro.pl/listing?string=', 'div.mpof_ki myre_zn _9c44d_1Hxbq', 'h2.mgn2_14 m9qz_yp mqu1_16 mp4t_0 m3h2_0 mryx_0 munh_0 mp4t_0 m3h2_0 mryx_0 munh_0 a', 'True', 'h1', 'div._1svub _lf05o _9a071_2MEB_']
]

sites = []
for row in siteData:
    sites.append(Website(row[0], row[1], row[2],
                         row[3], row[4], row[5], row[6], row[7]))

models = ['Olympus XA', 'Yashica T', 'Konica Big Mini']
for model in models:
    for targetSite in sites:
        main.search(model, targetSite)