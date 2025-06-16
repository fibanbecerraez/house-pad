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
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

def run_process():
    # Constantes
    COMPRA_ALQUILER = ['alquiler']
    BARRIO = ['capital-federal']
    PAGINA = 1
    
    # Estadísticas
    total_propiedades = 0
    propiedades_exitosas = 0
    propiedades_fallidas = 0
        
    try:
        logging.info("Iniciando el proceso de scraping...")
        # Inicializar en incognito
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        logging.info("Configurando el navegador...")
        driver = uc.Chrome(options=options)

        # Variables
        df_properties = pd.DataFrame(columns=['ID','URL','CALLE','BARRIO','INFO', 'MONEDA', 'PRECIO_ORIGINAL', 'FECHA_INGRESO', 'METROS', 'AMBIENTES', 'DORMITORIOS', 'BANOS', 'COCHERA'])
        contador = PAGINA
        
        while True:
            logging.info(f"Procesando página {contador}...")
            # Obtener informacion de la pagina
            soup = get_html.get_info(COMPRA_ALQUILER, BARRIO, contador, driver)
            
            anuncios = soup.find_all("div", class_="postingsList-module__card-container")
            logging.info(f"Encontrados {len(anuncios)} anuncios en la página {contador}")
            total_propiedades += len(anuncios)
            
            for anuncio in anuncios:
                try:
                    price, currency = get_property_information.get_price(anuncio)
                    link = get_property_information.get_link(anuncio)
                    address, neighborhood = get_property_information.get_location(anuncio)
                    info, metros, ambientes, dormitorios, banos, cochera = get_property_information.get_house_information(anuncio)
                    id = get_property_information.get_id(anuncio)            
                    df_properties.loc[len(df_properties)] = [id, link, address, neighborhood, info, currency, price, today, metros, ambientes, dormitorios, banos, cochera]
                    propiedades_exitosas += 1
                    logging.info(f"Propiedad procesada exitosamente: {address} - {price} {currency}")

                except Exception as e:
                    propiedades_fallidas += 1
                    logging.error(f"Error procesando una propiedad: {str(e)}")
                    continue
            
            # Guardar datos después de cada página
            if len(df_properties) > 0:
                export_info.save_info(df_properties)
                logging.info(f"Datos guardados después de la página {contador}")
                df_properties = pd.DataFrame(columns=['ID','URL','CALLE','BARRIO','INFO', 'MONEDA', 'PRECIO_ORIGINAL', 'FECHA_INGRESO', 'METROS', 'AMBIENTES', 'DORMITORIOS', 'BANOS', 'COCHERA'])
            
            # Chequear si hay una proxima pagina
            div_tag = soup.find("div", class_="paging-module__container-paging")
            if div_tag:
                links_data = [{"text": a.get_text(strip=False), "href": a["href"], "data_qa": a.get("data-qa", "")} for a in div_tag.find_all("a")]
                if any(link["data_qa"] == "PAGING_NEXT" for link in links_data):
                    contador = contador + 1
                    logging.info("Hay más páginas, continuando...")
                else:
                    logging.info("No hay más páginas, finalizando...")
                    break
            else:
                logging.warning("No se encontró el contenedor de paginación, finalizando...")
                break

        logging.info(f"""
        Proceso completado:
        - Total de propiedades encontradas: {total_propiedades}
        - Propiedades procesadas exitosamente: {propiedades_exitosas}
        - Propiedades con error: {propiedades_fallidas}
        - Tasa de éxito: {(propiedades_exitosas/total_propiedades)*100:.2f}%
        """)
        
    except Exception as e:
        logging.error(f"Error durante el proceso: {str(e)}")
    
    finally:
        logging.info("Cerrando el navegador...")
        driver.quit()

if __name__ == "__main__":
    run_process()