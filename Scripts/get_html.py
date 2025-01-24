from selenium import webdriver
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc

def get_info(compra_alquiler, barrio, contador, driver):
    # Definir si compra y/o alquiler
    compra_alquiler = '-'.join(compra_alquiler) if len(compra_alquiler) > 1 else compra_alquiler[0]

    # Definir barrio
    barrio = '-'.join(barrio) if len(barrio) > 1 else barrio[0]

    #GET webpage
    if contador == None:
        url = f"https://www.zonaprop.com.ar/departamentos-{compra_alquiler}-{barrio}.html"
    else:
        url = f"https://www.zonaprop.com.ar/departamentos-{compra_alquiler}-{barrio}-pagina-{contador}.html"

    time.sleep(3)
    driver.get(url)
    html = driver.page_source
    
    # Usar BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(html, "html.parser")

    return soup