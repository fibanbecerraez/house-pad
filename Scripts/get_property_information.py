from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

def get_price(anuncio):
    precio = anuncio.find_all("div", class_="postingPrices-module__price")
    price_text = precio[0].next.strip() if precio[0].next else ""
    currency, price_text = price_text.split(" ")
    price_text = price_text.replace('.', '')

    return price_text, currency

def get_location(anuncio):
    adress = anuncio.find_all("div", class_="postingLocations-module__location-address postingLocations-module__location-address-in-listing")
    adress = adress[0].next.strip() if adress[0].next else ""

    neighborhood = anuncio.find_all("h2", class_="postingLocations-module__location-text")
    neighborhood = neighborhood[0].next.strip() if neighborhood[0].next else ""

    return adress, neighborhood

def parse_house_info(info_str):
    metros = ambientes = dormitorios = banos = cochera = None
    # Metros
    m = re.search(r'(\d+) m²', info_str)
    if m:
        metros = int(m.group(1))
    # Ambientes
    m = re.search(r'(\d+) amb', info_str)
    if m:
        ambientes = int(m.group(1))
    # Dormitorios (siempre que aparezca en el string)
    m = re.search(r'(\d+) dorm', info_str)
    if m:
        dormitorios = int(m.group(1))
    # Baños
    m = re.search(r'(\d+) baño', info_str)
    if m:
        banos = int(m.group(1))
    # Cochera
    m = re.search(r'(\d+) coch', info_str)
    if m:
        cochera = int(m.group(1))
    elif 'coch' in info_str:
        cochera = 1
    return metros, ambientes, dormitorios, banos, cochera

def get_house_information(anuncio):
    h3_tag = anuncio.find("h3", class_="postingMainFeatures-module__posting-main-features-block")
    if not h3_tag:
        print("[DEBUG] No se encontró el tag <h3> de main features en el anuncio.")
        return '', None, None, None, None, None
    span_texts = [span.get_text() for span in h3_tag.find_all("span")]
    if not span_texts:
        print("[DEBUG] No se encontraron <span> dentro del <h3> de main features.")
        return '', None, None, None, None, None
    list_to_str = ' - '.join(span_texts)
    list_to_str = list_to_str.replace(".", "")
    print(f"[DEBUG] INFO extraído: {list_to_str}")
    metros, ambientes, dormitorios, banos, cochera = parse_house_info(list_to_str)
    print(f"[DEBUG] Parsed: metros={metros}, ambientes={ambientes}, dormitorios={dormitorios}, banos={banos}, cochera={cochera}")
    return list_to_str, metros, ambientes, dormitorios, banos, cochera

def get_link(anuncio):
    link = str(anuncio.find_all("div", class_="postingCardLayout-module__posting-card-layout"))
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