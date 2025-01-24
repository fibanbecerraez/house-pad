from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

def get_price(anuncio):
    precio = anuncio.find_all("div", class_="postingPrices-module__price__fqpP5")
    price_text = precio[0].next.strip() if precio[0].next else ""
    currency, price_text = price_text.split(" ")
    price_text = price_text.replace('.', '')

    return price_text, currency

def get_location(anuncio):
    adress = anuncio.find_all("div", class_="postingLocations-module__location-address__k8Ip7 postingLocations-module__location-address-in-listing__UQS03")
    adress = adress[0].next.strip() if adress[0].next else ""

    neighborhood = anuncio.find_all("h2", class_="postingLocations-module__location-text__Y9QrY")
    neighborhood = neighborhood[0].next.strip() if neighborhood[0].next else ""

    return adress, neighborhood

def get_house_information(anuncio):
    # Find the <h3> tag with the specified class
    h3_tag = anuncio.find("h3", class_="postingMainFeatures-module__posting-main-features-block__se1F_")

    # Extract text from all <span> tags within the <h3> tag
    span_texts = [span.get_text() for span in h3_tag.find_all("span")]
    list_to_str = ' - '.join(span_texts)
    list_to_str = list_to_str.replace(".", "")

    return list_to_str

def get_link(anuncio):
    link = str(anuncio.find_all("div", class_="postingCardLayout-module__posting-card-layout__Lklt9"))
    match = re.search(r'data-to-posting="([^"]+)"', link)
    if match:
        data_to_posting_url = match.group(1)
        url = "https://www.zonaprop.com.ar" + data_to_posting_url
    else:
        print("data-to-posting URL not found.")

    return url
    
def get_id(anuncio):
    data_id = anuncio.find('div', {'data-id': True})['data-id']
    return data_id