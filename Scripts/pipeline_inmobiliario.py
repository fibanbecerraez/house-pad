import pandas as pd
import os
from datetime import datetime
import numpy as np

# Paths
SCRAPING_PATH = os.path.join('Files', 'original_info.xlsx')
ADD_DATA_PATH = 'Add_Data'
OUTPUT_PATH = 'output'
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Archivos complementarios
MI_DAP_AX01_PATH = os.path.join(ADD_DATA_PATH, 'MI_DAP_AX01.xlsx')  # Precio promedio por barrio y periodo
MI_DAP_AX15_PATH = os.path.join(ADD_DATA_PATH, 'MI_DAP_AX15.xlsx')  # Precio promedio por ambiente y periodo
MI_DAN_AX03_PATH = os.path.join(ADD_DATA_PATH, 'MI_DAN_AX03.xlsx')  # Índice de precio m2 por ambiente y periodo

# 1. Cargar scraping
print('Cargando datos de scraping...')
df_scraping = pd.read_excel(SCRAPING_PATH)
df_scraping.columns = [c.lower() for c in df_scraping.columns]

# 2. Cargar MI_DAP_AX01 (hoja Tabla2)
print('Cargando MI_DAP_AX01 (precio promedio por barrio y periodo)...')
df_ax01 = pd.read_excel(MI_DAP_AX01_PATH, sheet_name='Tabla2')
df_ax01.columns = [c.lower() for c in df_ax01.columns]

def parse_periodo(periodo):
    try:
        return datetime.strptime(periodo, '%b-%Y')
    except Exception:
        return pd.NaT

df_ax01['fecha'] = df_ax01['atributo'].apply(parse_periodo)

# 3. Cargar MI_DAP_AX15 (precio promedio por ambiente y periodo)
print('Cargando MI_DAP_AX15 (precio promedio por ambiente y periodo)...')
df_ax15_raw = pd.read_excel(MI_DAP_AX15_PATH, sheet_name=0, header=None)
# Usar la segunda fila como header real
new_header = df_ax15_raw.iloc[0].tolist()
df_ax15 = df_ax15_raw[1:]
df_ax15.columns = ['año', 'mes', '1 ambiente', '2 ambientes', '3 ambientes']
# Eliminar filas que no sean numéricas en año
df_ax15 = df_ax15[df_ax15['año'].apply(lambda x: str(x).isdigit())]
# Crear columna fecha
df_ax15['fecha'] = pd.to_datetime(df_ax15['año'].astype(str) + '-' + df_ax15['mes'].astype(str) + '-01', errors='coerce')
# Transformar a formato largo (melt)
df_ax15_long = df_ax15.melt(id_vars=['fecha'], value_vars=['1 ambiente', '2 ambientes', '3 ambientes'], var_name='ambientes', value_name='precio_prom_ambiente')
df_ax15_long['ambientes'] = df_ax15_long['ambientes'].str.extract(r'(\d)').astype(float)
print('Columnas de df_ax15_long:', df_ax15_long.columns.tolist())
print('Primeras filas de df_ax15_long:')
print(df_ax15_long.head())

# 4. Cargar MI_DAN_AX03 (índice de precio m2 por ambiente y periodo)
print('Cargando MI_DAN_AX03 (índice de precio m2 por ambiente y periodo)...')
df_ax03_raw = pd.read_excel(MI_DAN_AX03_PATH, sheet_name=0, header=None)
# Usar la primera fila como header real
df_ax03 = df_ax03_raw[1:]
df_ax03.columns = ['año', 'mes'] + [str(c) for c in df_ax03_raw.iloc[0,2:]]
# Eliminar filas que no sean numéricas en año
df_ax03 = df_ax03[df_ax03['año'].apply(lambda x: str(x).isdigit())]
# Crear columna fecha
df_ax03['fecha'] = pd.to_datetime(df_ax03['año'].astype(str) + '-' + df_ax03['mes'].astype(str) + '-01', errors='coerce')
# Transformar a formato largo (melt)
df_ax03_long = df_ax03.melt(id_vars=['fecha'], value_vars=[c for c in df_ax03.columns if c not in ['año','mes','fecha']], var_name='ambientes', value_name='indice_precio_m2')
df_ax03_long['ambientes'] = df_ax03_long['ambientes'].str.extract(r'(\d)').astype(float)
print('Columnas de df_ax03_long:', df_ax03_long.columns.tolist())
print('Primeras filas de df_ax03_long:')
print(df_ax03_long.head())

# 5. Procesar fecha en scraping a mes/año para merge
fecha_scraping = next((col for col in df_scraping.columns if 'fecha' in col), None)
df_scraping['fecha'] = pd.to_datetime(df_scraping[fecha_scraping]).dt.to_period('M').dt.to_timestamp()

# 6. Merge principal: scraping + MI_DAP_AX01 (por barrio y fecha)
df_merged = pd.merge(
    df_scraping,
    df_ax01[['barrio', 'fecha', 'valor']],
    how='left',
    left_on=['barrio', 'fecha'],
    right_on=['barrio', 'fecha']
)
df_merged = df_merged.rename(columns={'valor': 'precio_prom_barrio'})

# 7. Merge con MI_DAP_AX15 (por fecha y ambientes)
if 'ambientes' in df_merged.columns:
    df_merged = pd.merge(
        df_merged,
        df_ax15_long[['fecha', 'ambientes', 'precio_prom_ambiente']],
        how='left',
        on=['fecha', 'ambientes']
    )

# 8. Merge con MI_DAN_AX03 (por fecha y ambientes)
if 'ambientes' in df_merged.columns:
    df_merged = pd.merge(
        df_merged,
        df_ax03_long[['fecha', 'ambientes', 'indice_precio_m2']],
        how='left',
        on=['fecha', 'ambientes']
    )

# 9. Calcular métricas de comparación
df_merged['precio_m2_scraping'] = df_merged['precio_original'] / df_merged['metros']
df_merged['diferencia_vs_prom_barrio'] = df_merged['precio_original'] - df_merged['precio_prom_barrio']
df_merged['diferencia_vs_prom_ambiente'] = df_merged['precio_original'] - df_merged['precio_prom_ambiente']
df_merged['indice_sobrevaloracion'] = df_merged['precio_m2_scraping'] / df_merged['indice_precio_m2']

# 10. Exportar resultado
df_merged.to_excel(os.path.join(OUTPUT_PATH, 'dataset_enriquecido.xlsx'), index=False)
print('Exportado: output/dataset_enriquecido.xlsx')

# 11. Documentar variables y fuentes
doc = '''
Variables y fuentes:
- precio_original: Precio de publicación de la propiedad (scraping, Zonaprop)
- precio_prom_barrio: Precio promedio de alquiler mensual por barrio y período (MI_DAP_AX01)
- precio_prom_ambiente: Precio promedio de alquiler mensual por cantidad de ambientes y período (MI_DAP_AX15)
- indice_precio_m2: Índice de precio promedio del m² de departamentos en alquiler por cantidad de ambientes y período (MI_DAN_AX03)
- diferencia_vs_prom_barrio: Diferencia entre precio de publicación y promedio del barrio
- diferencia_vs_prom_ambiente: Diferencia entre precio de publicación y promedio por ambiente
- indice_sobrevaloracion: Relación entre precio m2 scraping e índice histórico

Fuentes:
- MI_DAP_AX01: Dirección General de Estadística y Censos (GCBA), Buscainmueble, Adinco, Argenprop
- MI_DAP_AX15: Dirección General de Estadística y Censos (GCBA), Buscainmueble, Adinco, Argenprop
- MI_DAN_AX03: Instituto de Estadística y Censos de la Ciudad Autónoma de Buenos Aires
'''
with open(os.path.join(OUTPUT_PATH, 'documentacion_variables.txt'), 'w', encoding='utf-8') as f:
    f.write(doc)
print('Documentación generada en output/documentacion_variables.txt') 