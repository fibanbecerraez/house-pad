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
    
    # Cargar datos existentes si existen
    if os.path.exists(original_path):
        df_existing = pd.read_excel(original_path)
        print(f"Datos existentes cargados: {len(df_existing)} registros")
        
        # Combinar datos existentes con nuevos, evitando duplicados por ID
        df_combined = pd.concat([df_existing, df_properties])
        df_combined = df_combined.drop_duplicates(subset=['ID'], keep='last')
        print(f"Datos combinados: {len(df_combined)} registros (después de eliminar duplicados)")
        
        # Guardar datos combinados
        df_combined.to_excel(original_path, index=False)
        print(f"Datos guardados en {original_path}")
        
        # Actualizar time_price
        df_time_price = df_combined.copy()
        df_time_price = df_time_price.drop(columns=['URL','CALLE','BARRIO','INFO','MONEDA','METROS','AMBIENTES','DORMITORIOS','BANOS','COCHERA'])
        df_time_price = df_time_price.rename(columns={'FECHA_INGRESO': 'FECHA_PRECIO'})
        df_time_price['ID'] = df_time_price['ID'].astype(str)
        df_time_price.to_excel(time_price_path, index=False)
        print(f"Datos de precios guardados en {time_price_path}")
    else:
        # Si no existe el archivo, crear uno nuevo
        df_properties.to_excel(original_path, index=False)
        print(f"Nuevo archivo creado en {original_path} con {len(df_properties)} registros")
        
        # Crear time_price
        df_time_price = df_properties.copy()
        df_time_price = df_time_price.drop(columns=['URL','CALLE','BARRIO','INFO','MONEDA','METROS','AMBIENTES','DORMITORIOS','BANOS','COCHERA'])
        df_time_price = df_time_price.rename(columns={'FECHA_INGRESO': 'FECHA_PRECIO'})
        df_time_price['ID'] = df_time_price['ID'].astype(str)
        df_time_price.to_excel(time_price_path, index=False)
        print(f"Nuevo archivo de precios creado en {time_price_path}")




    
