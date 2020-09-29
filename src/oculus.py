import requests
import json
import time
from bs4 import BeautifulSoup


class Content:
    """Contains all variables/methods related to given content on a single website."""
    def __init__(self, model, price, url):
        self.model = model
        self.price = price
        self.url = url
    
    def print(self):
        print(f"Model: {self.model} - Price: {self.price} - \nURL: {self.url}\n")


class Website:
    """Contains all necessary variables related to a particular website."""
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
    """Contains the main logic of the program, including scraping the given websites."""
    def __init__(self):
        self.load_data()


    # Sends a request to the given url with a header, if response is OK - return object with lxml parser.
    def getPage(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if not response.ok:
            if response.status_code == 429:
                print("Rate limiting (allegro) - waiting 7 seconds...\n")
                time.sleep(7) # very unpythonic - will think of an alternative soon
            elif response.status_code != 429:
                print('Server responded:', response.status_code)
        else:
            return BeautifulSoup(response.text, 'lxml')


    # Checks whether parsed selector exists, if exists return if not return empty string.
    def safeGet(self, pageObj, selector):
        childObj = pageObj.select(selector)
        if childObj is not None and len(childObj) > 0:
            return childObj[0].get_text()
        else:
            return ""

    # Specific camera model and site are parsed into search,
    # then are searched for and if model and price variables are
    # not empty - return them via Content's print() method.
    def search(self, model, site):
        bs = self.getPage(site.searchURL + model)
        searchResults = bs.select(site.resultListing)
        if site.name == "OLX" and bs.find("div", {"class": "emptynew"}):
            return ""
        else:
            for result in searchResults:
                url = result.select(site.resultURL)[0].attrs['href']
                if (site.absoluteURL):
                    bs = self.getPage(url)
                else:
                    bs = self.getPage(site.url + url)
                if bs is None:
                    return
                model = self.safeGet(bs, site.modelTag).strip()
                model_price = self.safeGet(bs, site.priceTag).strip()
                model_price = model_price.replace(' ', '')
                if site.name == "OLX":
                    price, currency = model_price.split('zł')
                elif site.name == "Allegro":
                    price, *args = model_price.split(',')
                if model != "" and price != "" and int(price) <= camera['max_price']:
                    content = Content(model, price, url)
                    content.print()

    # Load specific camera models from camera_config.json
    def load_data(self):
        global camera_config # will remove soon
        try:
            try:
                with open('./data/camera_config.json') as config:
                    camera_config = json.load(config)
            except FileNotFoundError:
                with open('../data/camera_config.json') as config:
                    camera_config = json.load(config)
        except FileNotFoundError:
            return "Camera config not found!"
    

    def load_site_data(self):
        siteData = [
        ['OLX', 'https://www.olx.pl/', 'https://www.olx.pl/oferty/q-', 'div.offer-wrapper', 'h3.margintop5 a', 'True', 'h1', 'div.pricelabel'],
        ['Allegro', 'https://allegro.pl/', 'https://allegro.pl/listing?string=', 'div.mpof_ki.mqen_m6.mp7g_oh.mh36_0.mvrt_0.mg9e_8.mj7a_8.m7er_k4', 'h2.mgn2_14.m9qz_yp.mqu1_16.mp4t_0.m3h2_0.mryx_0.munh_0.mp4t_0.m3h2_0.mryx_0.munh_0 a', 'True', 'h1', 'div._1svub._lf05o._9a071_2MEB_']
        ]

        sites = []
        for row in siteData:
            sites.append(Website(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        main.camera_search(sites)


    def camera_search(self, sites):
        global camera # will delete later - late @ night can't think how to parse fml.
        for camera in camera_config['cameras']:
            for targetSite in sites:
                main.search(camera['model'], targetSite)
    

    def monitor_stock(self, site):
        print("No cameras found... Monitoring!")
        for camera in camera_config['cameras']:
            bs = self.getPage(site.searchURL + camera['model'])
            new_camera_listing = bs.find("h3", {"class": "margintop5"})
            if new_camera_listing is not None:
                main.search(camera['model'], site)


if __name__ == '__main__':
    main = Main()
    main.load_site_data()
