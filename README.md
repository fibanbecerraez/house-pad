# house-pad

**Análisis y segmentación del mercado inmobiliario de CABA mediante scraping, datos públicos y clustering.**

---

## 🧩 Hipótesis
"Los inmuebles en alquiler en CABA pueden agruparse en segmentos de mercado distintos según sus características estructurales y su ubicación, permitiendo identificar zonas sobrevaloradas o emergentes."

## 🎯 Objetivo
Aplicar técnicas de clustering sobre un dataset enriquecido (scraping + datos públicos) para segmentar el mercado inmobiliario de CABA, detectar segmentos de propiedades similares y zonas atípicas.

---

## 📁 Estructura del proyecto

```
├── Add_Data/                # Datos complementarios (índices, precios históricos, etc.)
├── Files/                   # Datos obtenidos por scraping (Excel)
├── Scripts/                 # Scripts de scraping, procesamiento y pipeline
│   ├── scrap.py             # Webscraping de ZonaProp
│   ├── export_info.py       # Guardado de datos en Excel
│   ├── get_property_information.py # Extracción y parseo de info de cada anuncio
│   └── pipeline_inmobiliario.py    # Pipeline de análisis, clustering y exportación
├── output/                  # Archivos listos para Power BI
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Este archivo
```

---

## ⚙️ Instalación y uso rápido

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/fibanbecerraez/house-pad.git
   cd house-pad
   ```
2. **Instala las dependencias:**
   ```bash
   py -m pip install -r requirements.txt
   ```
3. **Ejecuta el scraping:**
   ```bash
   py Scripts/scrap.py
   ```
   > Esto generará los archivos Excel en `Files/`.
4. **Ejecuta el pipeline:**
   ```bash
   py Scripts/pipeline_inmobiliario.py
   ```
   > Esto generará los archivos listos para Power BI en `output/`.

---

## 🚀 Ejemplo de uso en Google Colab

Puedes analizar y enriquecer los datos desde Colab:

```python
# Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Clonar el repo
!git clone https://github.com/fibanbecerraez/house-pad.git
%cd house-pad

# Instalar dependencias
!pip install -r requirements.txt

# Leer y analizar los datos
import pandas as pd
df = pd.read_excel('Files/original_info.xlsx')
df.head()
```

---

## 📊 Integración con Power BI

1. Abre Power BI Desktop.
2. Importa los archivos de la carpeta `output/` (fact_table.xlsx, dim_fechas.xlsx, etc.).
3. Relaciona las tablas por sus claves (ej: barrio, fecha, tipo).
4. Sugerencias de visualizaciones:
   - Mapa por barrio y cluster
   - Gráfico de dispersión (precio vs m²)
   - Tabla por tipo de propiedad y segmento
   - Filtros por barrio, tipo, cluster, ambientes

---

## 📈 Técnicas de Minería de Datos
- **Clustering:** K-Means, DBSCAN
- **PCA:** Reducción de dimensiones
- **Outliers:** Isolation Forest
- **EDA:** Análisis exploratorio

---

## 👤 Créditos
- Autor: [Tu nombre o equipo]
- GitHub: [fibanbecerraez](https://github.com/fibanbecerraez)
- Inspiración: [CBossio/house-pad](https://github.com/CBossio/house-pad)

---

## 📬 Contacto
¿Dudas, sugerencias o mejoras? ¡Abre un issue o un pull request! 