import pandas as pd
import os

# Ruta a la carpeta Add_Data
add_data_path = '../Add_Data'

# Archivo específico a leer
file = 'usd_historic_price.xlsx'
file_path = os.path.join(add_data_path, file)

print(f"\nArchivo: {file}")
df = pd.read_excel(file_path)
print(df.head()) 