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
    COMPRA_ALQUILER = ['alquiler']
    BARRIO = ['villa-devoto']
    PAGINA = 1
        
    try:
        print("Iniciando el proceso de scraping...")
        # Inicializar en incognito
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        print("Configurando el navegador...")
        driver = uc.Chrome(options=options)

        # Variables
        df_properties = pd.DataFrame(columns=['ID','URL','CALLE','BARRIO','INFO', 'MONEDA', 'PRECIO_ORIGINAL', 'FECHA_INGRESO', 'METROS', 'AMBIENTES', 'DORMITORIOS', 'BANOS', 'COCHERA'])
        contador = PAGINA
        while True:
            print(f"\nProcesando página {contador}...")
            # Obtener informacion de la pagina
            soup = get_html.get_info(COMPRA_ALQUILER, BARRIO, contador, driver)
            
            anuncios = soup.find_all("div", class_="postingsList-module__card-container")
            print(f"Encontrados {len(anuncios)} anuncios en la página {contador}")
            
            for anuncio in anuncios:
                try:
                    price, currency = get_property_information.get_price(anuncio)
                    link = get_property_information.get_link(anuncio)
                    address, neighborhood = get_property_information.get_location(anuncio)
                    info, metros, ambientes, dormitorios, banos, cochera = get_property_information.get_house_information(anuncio)
                    id = get_property_information.get_id(anuncio)            
                    df_properties.loc[len(df_properties)] = [id, link, address, neighborhood, info, currency, price, today, metros, ambientes, dormitorios, banos, cochera]
                    print(f"Propiedad procesada: {address} - {price} {currency}")

                except Exception as e:
                    print(f"Error procesando una propiedad: {str(e)}")
                    continue
            
            # Chequear si hay una proxima pagina
            div_tag = soup.find("div", class_="paging-module__container-paging")
            if div_tag:
                links_data = [{"text": a.get_text(strip=False), "href": a["href"], "data_qa": a.get("data-qa", "")} for a in div_tag.find_all("a")]
                if any(link["data_qa"] == "PAGING_NEXT" for link in links_data):
                    contador = contador + 1
                    print("Hay más páginas, continuando...")
                else:
                    print("No hay más páginas, finalizando...")
                    break
            else:
                print("No se encontró el contenedor de paginación, finalizando...")
                break

        print(f"\nProceso completado. Se encontraron {len(df_properties)} propiedades en total.")
        export_info.save_info(df_properties)
        
    except Exception as e:
        print(f"Error durante el proceso: {str(e)}")
    
    finally:
        print("Cerrando el navegador...")
        driver.quit()

if __name__ == "__main__":
    run_process()