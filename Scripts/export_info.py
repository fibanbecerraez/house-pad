import pandas as pd
from datetime import datetime
today = datetime.today().strftime('%Y-%m-%d')
import os
FILES_PATH = os.path.join(os.getcwd(),r'Files')

def save_info(df_properties):
    # Definir columnas esperadas
    original_columns = ['ID','URL','CALLE','BARRIO','INFO', 'MONEDA', 'PRECIO_ORIGINAL', 'FECHA_INGRESO', 'METROS', 'AMBIENTES', 'DORMITORIOS', 'BANOS', 'COCHERA']
    time_price_columns = ['ID', 'PRECIO_ORIGINAL', 'FECHA_PRECIO']

    # Crear archivos si no existen
    original_path = os.path.join(FILES_PATH, r'original_info.xlsx')
    time_price_path = os.path.join(FILES_PATH, r'time_price.xlsx')
    if not os.path.exists(original_path):
        pd.DataFrame(columns=original_columns).to_excel(original_path, index=False)
    if not os.path.exists(time_price_path):
        pd.DataFrame(columns=time_price_columns).to_excel(time_price_path, index=False)

    # Sobrescribir los archivos con los nuevos datos
    df_properties.to_excel(original_path, index=False)
    df_time_price = df_properties.copy()
    df_time_price = df_time_price.drop(columns=['URL','CALLE','BARRIO','INFO','MONEDA','METROS','AMBIENTES','DORMITORIOS','BANOS','COCHERA'])
    df_time_price = df_time_price.rename(columns={'FECHA_INGRESO': 'FECHA_PRECIO'})
    df_time_price['ID'] = df_time_price['ID'].astype(str)
    df_time_price.to_excel(time_price_path, index=False)




    
