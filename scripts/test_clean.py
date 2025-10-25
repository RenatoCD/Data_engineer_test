# scripts/test_clean.py

import sys
from pathlib import Path
import pandas as pd

# Agrega la raíz del proyecto al path para importar main.py
sys.path.append(str(Path(__file__).resolve().parent.parent))

from main import clean_data

# Carpeta donde main.py genera los CSV
transactions_folder = Path("../transactions")  # desde scripts/ hacia la raíz

# Lista todos los CSV en la carpeta
csv_files = sorted(transactions_folder.glob("*.csv"))
if not csv_files:
    print("No se encontraron CSV en", transactions_folder)
    exit()

# Seleccionar el archivo más reciente
latest_file = csv_files[-1]
print(f"\n>>> Archivo más reciente: {latest_file.name}")
df = pd.read_csv(latest_file)

print("Columnas originales:", df.columns.tolist())
print("Tipos de datos originales:")
print(df.dtypes)
print("Valores nulos por columna:\n", df.isna().sum())

# Aplicar clean_data
df_clean = clean_data(df)

print("\n--- Resultado de clean_data ---")
print("Primeras filas:")
print(df_clean.head())
print("Tipos de datos después de limpieza:")
print(df_clean.dtypes)
print("Valores nulos por columna después de limpieza:\n", df_clean.isna().sum())
print("Cantidad de filas originales:", len(df))
print("Cantidad de filas después de limpieza:", len(df_clean))
