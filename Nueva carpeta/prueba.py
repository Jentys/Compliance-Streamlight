import pandas as pd

archivo_norma = "NOM-001-STPS-2008_diagnostico.xlsx"

try:
    df = pd.read_excel(archivo_norma, engine="openpyxl")
    print("✅ Archivo cargado correctamente")
    print(df.head())  # Muestra las primeras filas para verificar
except Exception as e:
    print(f"⚠️ Error al leer el archivo: {e}")