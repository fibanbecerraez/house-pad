import pandas as pd
from datetime import datetime
today = datetime.today().strftime('%Y-%m-%d')
import os
FILES_PATH = os.path.join(os.getcwd(),r'Files')

def save_info(df_properties):

    # Guardar nuevas publicaciones en la tabla original
    original_df = pd.read_excel(os.path.join(FILES_PATH,r'original_info.xlsx'))
    existing_ids = set(map(str, original_df['ID'].dropna().tolist()))
    new_ids = set(map(str, df_properties['ID'].dropna().tolist()))
    missing_ids = new_ids.difference(existing_ids)
    missing_data = df_properties[df_properties['ID'].astype(str).isin(missing_ids)]
    if not missing_data.empty:
        updated_df = pd.concat([original_df, missing_data], ignore_index=True)
        updated_df.to_excel(os.path.join(FILES_PATH,r'original_info.xlsx'), index=False)


    # Guardar en el historico de precios los nuevos valores
    time_df = pd.read_excel(os.path.join(FILES_PATH,r'time_price.xlsx'))
    df_time_price = df_properties.copy()
    df_time_price = df_time_price.drop(columns=['URL','CALLE','BARRIO','INFO','MONEDA'])
    df_time_price = df_time_price.rename(columns={'FECHA_INGRESO': 'FECHA_PRECIO'})
    df_time_price['ID'] = df_time_price['ID'].astype(str)
    time_df['ID'] = time_df['ID'].astype(str)

    # # Mirar duplicados (ID y FECHA_PRECIO)
    # duplicate_entries = pd.merge(
    #     df_time_price, 
    #     time_df, 
    #     how='inner', 
    #     on=['ID', 'FECHA_PRECIO']
    # )

    # if not duplicate_entries.empty:
    #     print("Duplicate entries found:")
    #     print(duplicate_entries)
    # else:
    #     print("No duplicate entries found.")

    # non_duplicates = pd.concat([df_time_price, duplicate_entries])
    # non_duplicates = non_duplicates.drop_duplicates(keep=False)
    # updated_time_df = pd.concat([time_df, non_duplicates])
    # updated_time_df["PRECIO"] = updated_time_df["PRECIO"].fillna(updated_time_df["PRECIO_ORIGINAL"])
    # updated_time_df = updated_time_df.drop(columns=['PRECIO_ORIGINAL'])
    final_df = pd.concat([time_df, df_time_price], ignore_index=True)
    final_df['ID'] = df_time_price['ID'].astype(str)
    final_df.to_excel(os.path.join(FILES_PATH,r'time_price.xlsx'), index=False)




    
