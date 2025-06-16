import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Paths
SCRAPING_PATH = os.path.join('Files', 'original_info.xlsx')
ADD_DATA_PATH = 'Add_Data'
OUTPUT_PATH = 'output'
os.makedirs(OUTPUT_PATH, exist_ok=True)

def load_data():
    """Carga y unifica todos los datasets necesarios"""
    print("Cargando datos...")
    
    # Cargar datos de scraping
    df_scraping = pd.read_excel(SCRAPING_PATH)
    
    # Cargar datos complementarios
    df_dolar = pd.read_excel(os.path.join(ADD_DATA_PATH, 'usd_historic_price.xlsx'))
    df_precios = pd.read_excel(os.path.join(ADD_DATA_PATH, 'Precio promedio de publicación (pesos) de departamentos en alquiler de 1 a 5 ambientes usados y a estrenar por barrio.xlsx'))
    df_actos = pd.read_excel(os.path.join(ADD_DATA_PATH, 'Actos Notariales anotados en el Registro de la Propiedad Inmueble Div Sheet AÑO.xls'))
    
    return df_scraping, df_dolar, df_precios, df_actos

def create_dimensions(df_scraping):
    """Crea tablas de dimensiones para Power BI"""
    print("Creando dimensiones...")
    
    # Buscar la columna de fecha
    fecha_col = None
    for col in df_scraping.columns:
        if col.lower() in ['fecha', 'fecha_ingreso', 'fecha_publicacion']:
            fecha_col = col
            break
    if fecha_col is None:
        raise ValueError("No se encontró una columna de fecha en el scraping. Esperado: 'fecha', 'FECHA_INGRESO' o 'FECHA_PUBLICACION'.")
    fechas = pd.DataFrame({
        'fecha': pd.date_range(start=df_scraping[fecha_col].min(), end=df_scraping[fecha_col].max())
    })
    
    # Dimensión de Barrios
    barrios = pd.DataFrame({'barrio': df_scraping['BARRIO'].unique()})
    
    # Dimensión de Tipos de Propiedad
    tipos = pd.DataFrame({'tipo': df_scraping['INFO'].apply(lambda x: str(x).split(' ')[0]).unique()})
    
    return fechas, barrios, tipos

def preprocess_data(df_scraping, df_dolar, df_precios, df_actos):
    """Preprocesa y enriquece los datos"""
    print("Preprocesando datos...")
    
    # Normalizar nombres de columnas a minúsculas para evitar errores
    df_scraping.columns = [col.lower() for col in df_scraping.columns]
    # Detectar y renombrar la columna de fecha a 'fecha'
    fecha_col = next((col for col in df_scraping.columns if 'fecha' in col), None)
    if not fecha_col:
        raise ValueError(f"No se encontró columna de fecha en el scraping. Columnas: {df_scraping.columns}")
    df_scraping = df_scraping.rename(columns={fecha_col: 'fecha'})
    # Buscar la columna de moneda y precio
    moneda_col = next((col for col in df_scraping.columns if 'moneda' in col), None)
    precio_col = next((col for col in df_scraping.columns if 'precio_original' in col or 'precio' in col), None)
    if not moneda_col or not precio_col:
        raise ValueError(f"No se encontraron las columnas esperadas en el scraping. Columnas: {df_scraping.columns}")
    # Convertir precios a USD si es necesario
    df_scraping['precio_usd'] = df_scraping.apply(
        lambda x: x[precio_col] / df_dolar.loc[df_dolar['fecha'] == x['fecha'], 'precio'].iloc[0]
        if x[moneda_col] == 'ARS' else x[precio_col],
        axis=1
    )
    
    # Calcular métricas para Power BI
    df_scraping['precio_m2'] = df_scraping['precio_usd'] / df_scraping['metros']
    df_scraping['precio_por_ambiente'] = df_scraping['precio_usd'] / df_scraping['ambientes']
    df_scraping['precio_por_dormitorio'] = df_scraping['precio_usd'] / df_scraping['dormitorios']
    
    # Agregar variables temporales
    df_scraping['mes'] = pd.to_datetime(df_scraping['fecha']).dt.month
    df_scraping['año'] = pd.to_datetime(df_scraping['fecha']).dt.year
    df_scraping['trimestre'] = pd.to_datetime(df_scraping['fecha']).dt.quarter
    
    # Unir con datos de precios promedio
    df_scraping = pd.merge(
        df_scraping,
        df_precios,
        on=['barrio', 'ambientes'],
        how='left'
    )
    
    return df_scraping

def perform_clustering(df):
    """Realiza clustering sobre los datos"""
    print("Realizando clustering...")
    
    # Preparar variables para clustering
    features = ['precio_usd', 'metros', 'ambientes', 'dormitorios', 'banos']
    X = df[features].copy()
    
    # Normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Aplicar PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # K-means
    kmeans = KMeans(n_clusters=4, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Agregar etiquetas descriptivas a los clusters
    cluster_means = df.groupby('cluster')['precio_usd'].mean()
    cluster_labels = {
        cluster_means.index[0]: 'Premium',
        cluster_means.index[1]: 'Económico',
        cluster_means.index[2]: 'Medio',
        cluster_means.index[3]: 'Alto'
    }
    df['cluster_label'] = df['cluster'].map(cluster_labels)
    
    return df

def prepare_powerbi_tables(df, fechas, barrios, tipos):
    """Prepara las tablas finales para Power BI"""
    print("Preparando tablas para Power BI...")
    
    # Tabla de Hechos (Fact Table)
    fact_table = df[[
        'fecha', 'barrio', 'tipo', 'precio_usd', 'precio_m2', 
        'precio_por_ambiente', 'precio_por_dormitorio', 'metros',
        'ambientes', 'dormitorios', 'banos', 'cluster', 'cluster_label'
    ]].copy()
    
    # Agregar IDs para relaciones
    fact_table = pd.merge(fact_table, barrios, on='barrio', how='left')
    fact_table = pd.merge(fact_table, tipos, on='tipo', how='left')
    
    # Calcular métricas agregadas por cluster
    cluster_metrics = df.groupby('cluster_label').agg({
        'precio_usd': ['mean', 'std', 'min', 'max'],
        'metros': ['mean', 'std'],
        'ambientes': 'mean',
        'dormitorios': 'mean',
        'banos': 'mean'
    }).round(2)
    
    # Calcular métricas por barrio
    barrio_metrics = df.groupby('barrio').agg({
        'precio_usd': ['mean', 'std', 'min', 'max'],
        'metros': ['mean', 'std'],
        'ambientes': 'mean'
    }).round(2)
    
    return {
        'fact_table': fact_table,
        'dim_fechas': fechas,
        'dim_barrios': barrios,
        'dim_tipos': tipos,
        'cluster_metrics': cluster_metrics,
        'barrio_metrics': barrio_metrics
    }

def export_to_powerbi(tables):
    """Exporta las tablas en formato optimizado para Power BI"""
    print("Exportando tablas para Power BI...")
    
    # Exportar cada tabla
    tables['fact_table'].to_excel(os.path.join(OUTPUT_PATH, 'fact_table.xlsx'), index=False)
    tables['dim_fechas'].to_excel(os.path.join(OUTPUT_PATH, 'dim_fechas.xlsx'), index=False)
    tables['dim_barrios'].to_excel(os.path.join(OUTPUT_PATH, 'dim_barrios.xlsx'), index=False)
    tables['dim_tipos'].to_excel(os.path.join(OUTPUT_PATH, 'dim_tipos.xlsx'), index=False)
    tables['cluster_metrics'].to_excel(os.path.join(OUTPUT_PATH, 'cluster_metrics.xlsx'))
    tables['barrio_metrics'].to_excel(os.path.join(OUTPUT_PATH, 'barrio_metrics.xlsx'))
    
    # Crear archivo de relaciones para Power BI
    with open(os.path.join(OUTPUT_PATH, 'powerbi_relationships.txt'), 'w') as f:
        f.write("""
Relaciones para Power BI:

1. fact_table[barrio_id] -> dim_barrios[barrio_id]
2. fact_table[tipo_id] -> dim_tipos[tipo_id]
3. fact_table[fecha] -> dim_fechas[fecha]

Métricas calculadas sugeridas:

1. Precio promedio por m² = AVERAGE(fact_table[precio_m2])
2. Precio promedio por ambiente = AVERAGE(fact_table[precio_por_ambiente])
3. Precio promedio por dormitorio = AVERAGE(fact_table[precio_por_dormitorio])
4. Cantidad de propiedades por cluster = COUNT(fact_table[cluster])
5. Precio promedio por barrio = AVERAGE(fact_table[precio_usd])
        """)

def main():
    # Cargar datos
    df_scraping, df_dolar, df_precios, df_actos = load_data()
    
    # Crear dimensiones
    fechas, barrios, tipos = create_dimensions(df_scraping)
    
    # Preprocesar
    df_processed = preprocess_data(df_scraping, df_dolar, df_precios, df_actos)
    
    # Clustering
    df_clustered = perform_clustering(df_processed)
    
    # Preparar tablas para Power BI
    tables = prepare_powerbi_tables(df_clustered, fechas, barrios, tipos)
    
    # Exportar para Power BI
    export_to_powerbi(tables)
    
    print("¡Proceso completado! Los archivos para Power BI se encuentran en la carpeta 'output'")

if __name__ == "__main__":
    main() 