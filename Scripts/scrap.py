from selenium import webdriver
from bs4 import BeautifulSoup
import time
import get_property_information 
import get_html
import undetected_chromedriver as uc
import pandas as pd
import export_info
from datetime import datetime
today = datetime.today().strftime('%Y-%m-%d')
import os

def run_process():
    
    # Constantes
    COMPRA_ALQUILER = ['venta']
    BARRIO = ['villa-devoto', 'villa-pueyrredon']
    PAGINA = 1
        
    try:
        # Inicializar en incognito
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = uc.Chrome(options=options)

        # Variables
        df_properties = pd.DataFrame(columns=['ID','URL','CALLE','BARRIO','INFO', 'MONEDA', 'PRECIO_ORIGINAL', 'FECHA_INGRESO'])
        contador = PAGINA
        while True:
            # Obtener informacion de la pagina
            soup = get_html.get_info(COMPRA_ALQUILER, BARRIO, contador, driver)
            
            anuncios = soup.find_all("div", class_="CardContainer-sc-1tt2vbg-5 fvuHxG")
            
            for anuncio in anuncios:
                try:
                    price, currency = get_property_information.get_price(anuncio)
                    link = get_property_information.get_link(anuncio)
                    address, neighborhood = get_property_information.get_location(anuncio)
                    info = get_property_information.get_house_information(anuncio)
                    id = get_property_information.get_id(anuncio)            
                    df_properties.loc[len(df_properties)] = [id, link, address, neighborhood, info, currency, price, today]

                except Exception as e:
                    #print(f"Error procesando una ubicacion: {e}")
                    continue
            
            # Chequear si hay una proxima pagina
            div_tag = soup.find("div", class_="Container-sc-n5babu-0")
            links_data = [{"text": a.get_text(strip=False), "href": a["href"], "data_qa": a.get("data-qa", "")} for a in div_tag.find_all("a")]
            if any(link["data_qa"] == "PAGING_NEXT" for link in links_data):
                contador = contador + 1
            else:
                break

        export_info.save_info(df_properties)

        
    
    finally:
        driver.quit()



if __name__ == "__main__":
    run_process()
    print("Process complete")