import requests
import json
import time
from bs4 import BeautifulSoup
from dhooks import Webhook, Embed
from colorama import Fore, Style, init


class Content:
    """Contains all variables/methods related to given content on a single website."""
    def __init__(self, model, price, url):
        """The __init__ method is responsible for acting as a constructor.
        
        Args:
            model (str): Given camera model.
            price (int): Given camera price for a specific model.
            url (str): The URL for the camera being searched on a specific site.
        
        """
        self.model = model
        self.price = price
        self.url = url
    
    def print(self):
        """Serves as a template for printing out found items to the CLI."""
        print(f"Model: {self.model} - Price: {self.price} - \nURL: {self.url}\n")


class Website:
    """Contains all necessary variables related to a particular website."""
    def __init__(self, name, url, searchURL, resultListing, 
                resultURL, modelTag, priceTag, stockCount, sortByNewest):
        """The __init__ method is responsible for acting as a constructor.
        
        Args:
            name (str): Name of the website being crawled.
            url (str): The main URL of the website.
            searchURL (str): The specific search URL.
            resultListing (str): CSS Tag for each listing on the website.
            resultURL (str): CSS Tag where the URL is inside.
            modelTag (str): CSS Tag where the model name is.
            priceTag (str): CSS Tag where the price for the model is.
            stockCount (str): CSS Tag for the stock count for the specific model.
            sortByNewest (str): Part of the URL which is responsible for sorting by newest.

        """
        self.name = name
        self.url = url
        self.searchURL = searchURL
        self.resultListing = resultListing
        self.resultURL = resultURL
        self.modelTag = modelTag
        self.priceTag = priceTag
        self.stockCount = stockCount
        self.sortByNewest = sortByNewest


class Main:
    """Contains the main logic of the program, including scraping the given websites."""
    def __init__(self):
        self.load_data()


    @staticmethod
    def getPage(url):
        """Responsible for sending a request to the website with the given headers.
        
        Args:
            url (str): The URL the request is to be sent to.

        Returns:
            BeautifulSoup: The BeautifulSoup4 object that contains the request response. 
        
        """

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
            response = requests.get(url, headers=headers)
            if not response.ok:
                if response.status_code == 429:
                    print("Rate limiting (allegro) - restarting...\n")
                    time.sleep(5)
                    main.monitor_stock()
                elif response.status_code != 429:
                    print('Server responded:', response.status_code)
                    main.monitor_stock()
            else:
                return BeautifulSoup(response.text, 'lxml')
        except:
            main.monitor_stock()


    @staticmethod
    def getSelector(soupObject, selector):
        """Gets the selector (CSS tag) from the given website.
        
        Args:
            soupObject (:obj:`str`): The BeautifulSoup4 object that contains the request response.
            selector (str): The CSS selector to be checked for.
        
        Returns:
            selectedTag: The text of the tag if found, else empty string.

        """
        selectedTag = soupObject.select(selector)
        if selectedTag is not None and len(selectedTag) >= 1:
            return selectedTag[0].get_text()
        else:
            return ""


    def search(self, model, site):
        """The scraper/finder part of the script, crawls through the listings, if a particular listing meets requirements, it gets printed out.
        
        Args:
            model (str): The current model of the camera to be searched for.
            site (:obj:`str`): The site object, containing all of the current sites information.

        Returns:
            Empty string if no listings for OLX, or if the BeautifulSoup4 object is None.

        """
        soupObject = self.getPage(site.searchURL + model)
        searchResults = soupObject.select(site.resultListing)
        if site.name == "OLX" and soupObject.find("div", {"class": "emptynew"}):
            return ""
        else:
            for result in searchResults:
                url = result.select(site.resultURL)[0].attrs['href']
                soupObject = self.getPage(url)
                if soupObject is None:
                    return ""
                model = self.getSelector(soupObject, site.modelTag).strip()
                model_price = self.getSelector(soupObject, site.priceTag).strip()
                model_price = model_price.replace(' ', '')
                if site.name == "OLX":
                    price, _ = model_price.split('zł')
                elif site.name == "Allegro":
                    price, *_ = model_price.split(',')
                if model != "" and price != "" and int(price) <= self.camera['max_price']:
                    content = Content(model, price, url)
                    content.print()


    def load_data(self):
        """Loads the camera config, containing the models to be searched for and the maximum allowed prices.
        
        Returns:
            An error message if the config isn't found anywhere.

        Raises:
            FileNotFoundError: If the file is not found, try another location, if that fails return error.

        """
        try:
            try:
                with open('./data/camera_config.json') as config:
                    self.camera_config = json.load(config)
            except FileNotFoundError:
                with open('../data/camera_config.json') as config:
                    self.camera_config = json.load(config)
        except FileNotFoundError:
            return "Camera config not found!"
    

    def load_site_data(self):
        """Loads the site data and passes them in as a Website object."""
        siteData = [
        ['OLX', 'https://www.olx.pl/', 'https://www.olx.pl/elektronika/fotografia/q-', 'div.offer-wrapper', 'h3.margintop5 a', 'h1', 'div.pricelabel', 'p.color-2', '?search%5Border%5D=created_at%3Adesc'],
        ['Allegro', 'https://allegro.pl/', 'https://allegro.pl/kategoria/fotografia?string=', 'div.mpof_ki.mqen_m6.mp7g_oh.mh36_0.mvrt_0.mg9e_8.mj7a_8.m7er_k4', 'h2.mgn2_14.m9qz_yp.mqu1_16.mp4t_0.m3h2_0.mryx_0.munh_0.mp4t_0.m3h2_0.mryx_0.munh_0 a', 'h1', 'div._1svub._lf05o._9a071_2MEB_', 'span._11fdd_39FjG', '&bmatch=baseline-product-cl-eyesa2-engag-dict45-ele-1-2-0717&order=n']
        ]

        self.sites = []
        for row in siteData:
            self.sites.append(Website(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        main.camera_search(self.sites)


    def camera_search(self, sites):
        """Given the mode by the user, it decides what option to pick - if the option was 1, the monitor else the scraper.
        
        Args:
            sites (list): All of the sites that have been loaded.
        
        """
        if self.mode == 2:
            for self.camera in self.camera_config['cameras']:
                for targetSite in self.sites:
                    main.search(self.camera['model'], targetSite)
        elif self.mode == 1:
            main.monitor_stock()
    

    def monitor_stock(self):
        """Continuously checks whether new items have been added, if found, sends a notification to Discord and to the CLI.
        
        Raises:
            IndexError: If the desired tag didn't work, raise IndexError and try another one.
        
        """
        print("\n\nMonitoring... loading stock...!")
        self.no_of_items = 0
        self.camera_item_dict = {}
        current_time = time.localtime()
        self.time = time.strftime("%H:%M:%S", current_time)
        for index, _ in enumerate(range(1, 100000)):
            if index == 0:
                main.load_stock()
                print("\nStock loaded... monitoring for changes!\n")
            else:
                for _ in range(0, 100000):
                    for self.camera in self.camera_config['cameras']:
                        for site in self.sites:
                            for key in self.camera_item_dict:
                                if site.name in key and self.camera['model'] in key:
                                    old_stock = self.camera_item_dict[key]
                            self.promoted = True
                            time.sleep(1) # bug with response status code 429 @ allegro - temp sleep (again)
                            soupObject = self.getPage(site.searchURL + self.camera['model'])
                            if site.name == "OLX":
                                soupObject = self.getPage(site.searchURL + self.camera['model'] + site.sortByNewest)
                                try:
                                    self.no_of_items = soupObject.select(site.stockCount)[0].text
                                except: 
                                    self.no_of_items = "Znaleziono 0 ogłoszeń"
                                array_of_ints = [s for s in self.no_of_items.split() if s.isdigit()]
                                self.no_of_items = "".join(array_of_ints)
                                if int(self.no_of_items) == int(old_stock):
                                    pass
                                elif int(self.no_of_items) > int(old_stock):
                                    searchResults = soupObject.select(site.resultListing)
                                    while self.promoted:
                                        for result in searchResults:
                                            url = result.select(site.resultURL)[0].attrs['href']
                                            if ";promoted" not in url:
                                                self.promoted = False
                                                break
                                            else:
                                                pass
                                    main.model_check(site, url)
                                elif int(self.no_of_items) < int(old_stock): 
                                    print("Stock count has been altered (bought/deleted items), restarting...\n")
                                    main.monitor_stock()
                            elif site.name == "Allegro":
                                soupObject = self.getPage(site.searchURL + self.camera['model'] + site.sortByNewest)
                                self.no_of_items = soupObject.select(site.stockCount)[0].text
                                self.no_of_items = self.no_of_items.replace(' ', '')
                                old_stock = old_stock.replace(' ', '')
                                if int(self.no_of_items) == int(old_stock):
                                    pass
                                elif int(self.no_of_items) > int(old_stock):
                                    section_obj_allegro = soupObject.find("section", {"class": "_9c44d_3pyzl"})
                                    header_non_promoted = soupObject.find("h2", string="Oferty")
                                    header_promoted = soupObject.find("h2", string="Oferty promowane")
                                    after_header_product_list = []
                                    ind_of_header = 0
                                    if header_promoted:
                                        for ind, all_obj in enumerate(section_obj_allegro):
                                            if all_obj == header_non_promoted:
                                                ind_of_header = ind
                                                break
                                            else:
                                                continue
                                        for ind, all_obj in enumerate(section_obj_allegro):
                                            if ind <= ind_of_header:
                                                pass
                                            else:
                                                after_header_product_list.append(all_obj)
                                    else:
                                        for all_obj in section_obj_allegro:
                                            after_header_product_list.append(all_obj)
                                        ind_of_header = 0
                                    while self.promoted:
                                        for result in after_header_product_list:
                                            try:
                                                url = result.select("div div div h2 a")[0].attrs['href']
                                            except IndexError:
                                                url = result.select("div div div div h2 a")[0].attrs['href']
                                            if "/events/" not in url:
                                                self.promoted = False
                                                break
                                            elif "/events/" in url:
                                                pass
                                    main.model_check(site, url)


    def model_check(self, site, url):
        """Checks whether the returned model is in the maximum price range.
        
        Args:
            site (:obj:`str`): The site object, containing all of the current sites information.
            url (str): The URL for the current website.

        """
        soupObject = self.getPage(url)
        model_price = self.getSelector(soupObject, site.priceTag).strip()
        if site.name == "OLX":
            price, _ = model_price.split('zł')
        else:
            try:
                price, *_ = model_price.split(',')
            except:
                price, *_ = model_price.split(' ')
        price = price.replace(' ', '')
        if int(price) <= self.camera['max_price']:
            print(f"Found new {self.camera['model']}, {site.name} at {self.time}\nURL: {url}, Price: {price}")
            main.webhook_embed(self.camera['model'], site, url, price)
            main.monitor_stock()
        else:
            print(f"Found product over the price limit at {site.name}... Restarting\n")
            main.monitor_stock()


    def load_stock(self):
        """Loads the current stock found for all cameras on all websites."""
        try:
            for self.camera in self.camera_config['cameras']:
                for site in self.sites:
                    soupObject = self.getPage(site.searchURL + self.camera['model'] + site.sortByNewest)
                    main.stock_check(self.camera, site, soupObject)
        except:
            print("An error has occurred when loading stock... Restarting...\n")
            main.monitor_stock()

    
    def stock_check(self, camera, site, soupObject):
        """Compares new stock, to the stock that has been loaded before hand.
        
        Args:
            camera (dict): Contains the camera model and max price.
            site (:obj:`str`): The site object, containing all of the current sites information.
            soupObject (:obj:`str`): The BeautifulSoup4 object that contains the request response.

        """
        try:
            if site.name == "OLX":
                try:
                    self.no_of_items = soupObject.select(site.stockCount)[0].text
                except:
                    self.no_of_items = "Znaleziono 0 ogłoszeń"
                array_of_ints = [s for s in self.no_of_items.split() if s.isdigit()]
                self.no_of_items = "".join(array_of_ints)
                key = f"{self.camera['model']}, {site.name}"
                self.camera_item_dict[key] = int(self.no_of_items)
            elif site.name == "Allegro":
                self.no_of_items = soupObject.select(site.stockCount)[0].text
                key = f"{self.camera['model']}, {site.name}"
                self.camera_item_dict[key] = self.no_of_items
        except:
            print("An error has occurred when checking stock... Restarting...\n")
            main.monitor_stock()


    def webhook_embed(self, camera, site, url, price):
        """Responsible for the Discord Webhook notification system.
        
        Args:
            camera (dict): Contains the camera model and max price.
            site (:obj:`str`): The site object, containing all of the current sites information.
            url (str): The URL for the current website.
            price (int): The price of the product.
        
        """
        hook = Webhook("#")

        embed = Embed(color=0x5CDBF0, timestamp='now')
        embed.set_author(name=f"FOUND NEW {self.camera['model']} @ {site.name}, PRICE: {price}PLN")
        embed.add_field(name='URL', value=f"{url}")
        embed.set_footer(text='POWERED BY OCULUSHOOK')

        hook.send(embed=embed)


    def select_mode(self):
        """Allows the user to pick the mode they want to use.
        
        Raises:
            ValueError: If the response provided by a user is not equal to 1 or 2, raise exception.
        
        """
        self.mode = 0
        print("")
        print(Fore.WHITE + Style.BRIGHT + "1. MONITOR")
        print(Fore.WHITE + Style.BRIGHT + "2. FINDER/SCRAPER (in progress)")
        while self.mode != 1 or self.mode != 2:
            user_input = input("\nWhich mode would you like to run?\n")
            try:
                self.mode = int(user_input)
            except ValueError:
                print("Please input either '1' or '2'.")
                continue
            if self.mode == 1 or self.mode == 2:
                main.load_site_data()


if __name__ == '__main__':
    init()
    print()
    print(Fore.CYAN + r"""
    _______  _______           _                 _______ 
    (  ___  )(  ____ \|\     /|( \      |\     /|(  ____ \
    | (   ) || (    \/| )   ( || (      | )   ( || (    \/
    | |   | || |      | |   | || |      | |   | || (_____ 
    | |   | || |      | |   | || |      | |   | |(_____  )
    | |   | || |      | |   | || |      | |   | |      ) |
    | (___) || (____/\| (___) || (____/\| (___) |/\____) |
    (_______)(_______/(_______)(_______/(_______)\_______)
                                                      
        """)
    print()

    main = Main()
    main.select_mode()
