import pandas as pd
import os
from datetime import datetime

# Paths
SCRAPING_PATH = os.path.join('Files', 'original_info.xlsx')
ADD_DATA_PATH = 'Add_Data'
MI_DAP_AX01_PATH = os.path.join(ADD_DATA_PATH, 'MI_DAP_AX01.xlsx')  # Ajusta el nombre si es necesario
OUTPUT_PATH = 'output'
os.makedirs(OUTPUT_PATH, exist_ok=True)

# 1. Cargar scraping
print('Cargando datos de scraping...')
df_scraping = pd.read_excel(SCRAPING_PATH)

# 2. Cargar MI_DAP_AX01, hoja Tabla2
print('Cargando datos de MI_DAP_AX01 (Tabla2)...')
df_mi_dap = pd.read_excel(MI_DAP_AX01_PATH, sheet_name='Tabla2')

# 3. Normalizar nombres de columnas
df_scraping.columns = [c.lower() for c in df_scraping.columns]
df_mi_dap.columns = [c.lower() for c in df_mi_dap.columns]

# 4. Procesar periodo en MI_DAP_AX01 a formato fecha (ej: "Abr-2011" -> datetime)
def parse_periodo(periodo):
    try:
        return datetime.strptime(periodo, '%b-%Y')
    except Exception:
        return pd.NaT

df_mi_dap['fecha'] = df_mi_dap['atributo'].apply(parse_periodo)

# 5. Procesar fecha en scraping a mes/año para merge
fecha_scraping = next((col for col in df_scraping.columns if 'fecha' in col), None)
df_scraping['fecha'] = pd.to_datetime(df_scraping[fecha_scraping]).dt.to_period('M').dt.to_timestamp()

# 6. Merge por barrio y fecha
print('Realizando merge por barrio y fecha (mes/año)...')
df_merged = pd.merge(
    df_scraping,
    df_mi_dap[['barrio', 'fecha', 'valor']],
    how='left',
    left_on=['barrio', 'fecha'],
    right_on=['barrio', 'fecha']
)

# 7. Exportar resultado
df_merged.to_excel(os.path.join(OUTPUT_PATH, 'dataset_enriquecido.xlsx'), index=False)
print('Exportado: output/dataset_enriquecido.xlsx')

# 8. Documentar fuente y definición
doc = '''
Fuente: Dirección General de Estadística y Censos (Ministerio de Hacienda y Finanzas GCBA) sobre la base de datos del sistema Buscainmueble (hasta septiembre 2011), Adinco (desde octubre 2011 hasta junio 2015) y Argenprop (a partir de julio 2015).

Variable: Precio promedio del alquiler mensual de los departamentos de 1 a 5 ambientes publicados (usados y a estrenar), expresado en pesos.
'''
with open(os.path.join(OUTPUT_PATH, 'documentacion_mi_dap_ax01.txt'), 'w', encoding='utf-8') as f:
    f.write(doc)
print('Documentación generada en output/documentacion_mi_dap_ax01.txt') 