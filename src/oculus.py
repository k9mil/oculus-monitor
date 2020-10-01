import requests
import json
import time
import oculus_discord
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
    def __init__(self, name, url, searchURL, resultListing, resultURL, modelTag, priceTag):
        self.name = name
        self.url = url
        self.searchURL = searchURL
        self.resultListing = resultListing
        self.resultURL = resultURL
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
                print("Rate limiting (allegro) - waiting 5 seconds...\n")
                time.sleep(5) # very unpythonic - will think of an alternative soon
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
                bs = self.getPage(url)
                if bs is None:
                    return
                model = self.safeGet(bs, site.modelTag).strip()
                model_price = self.safeGet(bs, site.priceTag).strip()
                model_price = model_price.replace(' ', '')
                if site.name == "OLX":
                    price, currency = model_price.split('zł')
                elif site.name == "Allegro":
                    price, *args = model_price.split(',')
                if model != "" and price != "" and int(price) <= self.camera['max_price']:
                    content = Content(model, price, url)
                    content.print()

    # Load specific camera models from camera_config.json
    def load_data(self):
        try:
            try:
                with open('./data/camera_config.json') as config:
                    self.camera_config = json.load(config)
            except FileNotFoundError:
                with open('../data/camera_config.json') as config:
                    self.camera_config = json.load(config)
        except FileNotFoundError:
            return "Camera config not found!"
    

    # Loads site data, declared a site list, appends the sites to the list and then calls camera_search() parsing the sites through.
    def load_site_data(self):
        siteData = [
        ['OLX', 'https://www.olx.pl/', 'https://www.olx.pl/oferty/q-', 'div.offer-wrapper', 'h3.margintop5 a.detailsLink', 'h1', 'div.pricelabel'],
        ['Allegro', 'https://allegro.pl/', 'https://allegro.pl/listing?string=', 'div.mpof_ki.mqen_m6.mp7g_oh.mh36_0.mvrt_0.mg9e_8.mj7a_8.m7er_k4', 'h2.mgn2_14.m9qz_yp.mqu1_16.mp4t_0.m3h2_0.mryx_0.munh_0.mp4t_0.m3h2_0.mryx_0.munh_0 a', 'h1', 'div._1svub._lf05o._9a071_2MEB_']
        ]

        self.sites = []
        for row in siteData:
            self.sites.append(Website(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        main.camera_search(self.sites)


    # if the mode chosen was equal to 2, it runs the search() function, if the mode was equal to 1, it runs the monitor_stock() function
    def camera_search(self, sites):
        if self.mode == 2:
            for self.camera in self.camera_config['cameras']:
                for targetSite in self.sites:
                    main.search(self.camera['model'], targetSite)
        elif self.mode == 1:
            main.monitor_stock()
    

    # monitors the stock for new additions to the given websites, for the given models.
    def monitor_stock(self):
        print("\n\nMonitoring... loading stock...!")
        self.no_of_items = 0
        self.camera_item_dict = {}
        self.new_item_url = ""
        current_time = time.localtime()
        self.time = time.strftime("%H:%M:%S", current_time)
        monitor = True
        for index, val in enumerate(range(1, 100000)):
            if index == 0:
                for self.camera in self.camera_config['cameras']:
                    for site in self.sites:
                        bs = self.getPage(site.searchURL + self.camera['model'])
                        if site.name == "OLX":
                            key = f"{self.camera['model']}, {site.name}"
                            self.no_of_items = bs.find("p", {"class": "color-2"}).text
                            array_of_ints = [s for s in self.no_of_items.split() if s.isdigit()]
                            self.no_of_items = "".join(array_of_ints)
                            self.camera_item_dict[key] = int(self.no_of_items)
                        elif site.name == "Allegro":
                            key = f"{self.camera['model']}, {site.name}"
                            self.no_of_items = bs.find("span", {"class": "_11fdd_39FjG"}).text
                            self.camera_item_dict[key] = self.no_of_items
                print("\nStock loaded... monitoring for changes!\n")
            else:
                try:
                    for i in range(0, 100000):
                        for self.camera in self.camera_config['cameras']:
                            for site in self.sites:
                                for key in self.camera_item_dict:
                                    if site.name in key and self.camera['model'] in key:
                                        old_stock = self.camera_item_dict[key]
                                time.sleep(2) # bug with response status code 429 @ allegro - temp sleep (again)
                                bs = self.getPage(site.searchURL + self.camera['model'])
                                if site.name == "OLX":
                                    self.no_of_items = bs.find("p", {"class": "color-2"}).text
                                    array_of_ints = [s for s in self.no_of_items.split() if s.isdigit()]
                                    self.no_of_items = "".join(array_of_ints)
                                    if int(self.no_of_items) == int(old_stock):
                                        pass
                                    elif int(self.no_of_items) > int(old_stock):
                                        self.new_item_url = (site.searchURL + self.camera['model'] + "?search%5Border%5D=created_at%3Adesc")
                                        print(f"Found new {self.camera['model']}, {site.name} at {self.time}\nURL: {self.new_item_url}")
                                        main.monitor_stock()
                                    elif int(self.no_of_items) < int(old_stock): 
                                        print("Stock count has been altered (bought/deleted items), restarting...\n")
                                        main.monitor_stock()
                                elif site.name == "Allegro":
                                    self.no_of_items = bs.find("span", {"class": "_11fdd_39FjG"}).text
                                    self.no_of_items = self.no_of_items.replace(' ', '')
                                    old_stock = old_stock.replace(' ', '')
                                    if int(self.no_of_items) == int(old_stock):
                                        pass
                                    elif int(self.no_of_items) > int(old_stock):
                                        self.new_item_url = (site.searchURL + self.camera['model'] + "&bmatch=baseline-product-cl-eyesa2-engag-dict45-ele-1-2-0717&order=n")
                                        print(f"Found new {self.camera['model']}, {site.name} at {self.time}\nURL: {self.new_item_url}")
                                        main.monitor_stock()
                                    elif int(self.no_of_items) < int(old_stock):
                                        print("Stock count has been altered (bought/deleted items), restarting...\n")
                                        main.monitor_stock()
                except:
                    print("An error has occurred, restarting...\n")
                    main.monitor_stock()

    # allows the user to select the mode they want to pick, either the scraper or the monitor.
    def select_mode(self):
        self.mode = 0
        print("1. MONITOR (in progress)")
        print("2. FINDER/SCRAPER (in progress)")
        while self.mode != 1 or self.mode != 2:
            user_input = input("Which mode would you like to run?\n")
            try:
                self.mode = int(user_input)
            except ValueError:
                print("Please input either '1' or '2'.")
                continue
            if self.mode == 1 or self.mode == 2:
                main.load_site_data()



if __name__ == '__main__':
    main = Main()
    main.select_mode()
