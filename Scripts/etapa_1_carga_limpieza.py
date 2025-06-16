"""
Etapa 1: Carga y limpieza de datos
- Carga los datasets principales y complementarios
- Normaliza nombres de barrios y periodos
- Guarda los dataframes limpios para la siguiente etapa
Adaptado para Google Colab.
"""

import pandas as pd
import os

# Definir rutas absolutas para Google Colab
BASE_PATH = '/content/drive/MyDrive/house-pad'
SCRAPING_PATH = f'{BASE_PATH}/Files/original_info.xlsx'
ADD_DATA_PATH = f'{BASE_PATH}/Add_Data'

def cargar_datos_scraping():
    """Carga el dataset principal del scraping."""
    df = pd.read_excel(SCRAPING_PATH)
    print('\n[Scraping] Primeras filas:')
    print(df.head())
    print('\n[Scraping] Info:')
    print(df.info())
    if 'barrio' in df.columns:
        print('\n[Scraping] Barrios únicos:', df['barrio'].unique())
    if 'periodo' in df.columns:
        print('\n[Scraping] Periodos únicos:', df['periodo'].unique())
    return df

def cargar_datos_complementarios():
    """Carga los datasets de Add_Data y los muestra."""
    excel_files = [f for f in os.listdir(ADD_DATA_PATH) if f.endswith('.xlsx')]
    dfs = {}
    for file in excel_files:
        file_path = os.path.join(ADD_DATA_PATH, file)
        df = pd.read_excel(file_path)
        print(f'\n[{file}] Primeras filas:')
        print(df.head())
        print(f'[{file}] Info:')
        print(df.info())
        dfs[file] = df
    return dfs

def normalizar_barrios(df):
    """Normaliza los nombres de barrios."""
    # Implementar luego
    return df

def normalizar_periodos(df):
    """Normaliza los periodos/fechas a un formato estándar."""
    # Implementar luego
    return df

if __name__ == "__main__":
    # 1. Cargar datasets
    df_scraping = cargar_datos_scraping()
    dfs_complementarios = cargar_datos_complementarios()
    # 2. (Próximo paso) Normalizar columnas clave
    # 3. (Próximo paso) Guardar dataframes limpios 