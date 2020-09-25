import requests
from bs4 import BeautifulSoup


class Oculus_Olx:
    def olx_model_data(soup):
        try:
            model = soup.find('h1').text.strip()
        except:
            model = ""
        try:
            p = soup.find('div', class_="pricelabel").text.strip()
            price, currency = p.split(' ')
        except:
            price = ""
        
        data = {'model' : model, 'price': price}
        return data

    def olx_index(soup):
        try:
            links = soup.find_all('a', class_="marginright5")
        except:
            links = []
        urls = [link.get('href') for link in links]
        return urls


class Oculus_Allegro:
    def allegro_model_data(soup):
        try:
            model = soup.find('h1').text.strip()
        except:
            model = ""
        try:
            price = soup.find('div', class_="_1svub _lf05o _9a071_2MEB_")
        except:
            price = ""
        
        data = {'model' : model, 'price': price}
        return data
    

    def allegro_index(soup):
        try:
            links = soup.find_all('a', class_="_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY")
        except:
            links = []
        urls = [link.get('href') for link in links]
        return urls


class Main:
    def get_page(url):
        response = requests.get(url)
        if not response.ok:
            print('Server responded:', response.status_code)
        else:
            soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def main():
        olx_models = ["https://www.olx.pl/oferty/q-olympus-trip/",
        "https://www.olx.pl/oferty/q-olympus-xa/",
        "https://www.olx.pl/oferty/q-olympus-mju/",
        "https://www.olx.pl/oferty/q-yashica-t/",
        "https://www.olx.pl/oferty/q-konica-big-mini/"]

        allegro_models = ["https://allegro.pl/listing?string=olympus%20trip", 
        "https://allegro.pl/listing?string=olympus%20xa",
        "https://allegro.pl/listing?string=olympus%20mju",
        "https://allegro.pl/listing?string=yashica%20t",
        "https://allegro.pl/listing?string=konica%20big%20mini"]

        print("OLX: \n")
        for model in olx_models:
            products = Oculus_Olx.olx_index(Main.get_page(model))
            for link in products:
                data = Oculus_Olx.olx_model_data(Main.get_page(link))
                print(data)
        
        print("\nALLEGRO: \n")
        for model in allegro_models:
            products = allegro_index(Main.get_page(model))
            for link in products:
                data = allegro_model_data(Main.get_page(link))
                print(data)

Main.main()