import pandas as pd
from pathlib import Path


folder = Path(__file__).parent.parent / "transactions"
folder = folder.resolve()
if not folder.exists():
    raise FileNotFoundError(f"La carpeta '{folder}' no existe.")
files = list(folder.glob("*.csv"))
print("Archivos encontrados:", files)

# Leer los primeros 1-2 archivos para inspección
for f in files[:2]:
    print("\n>>> Archivo:", f.name)
    df = pd.read_csv(f)
    print("Columnas:", df.columns.tolist())
    print("Primeras filas:")
    print(df.head())
    print("Tipos de datos:")
    print(df.dtypes)
    print("Valores nulos por columna:")
    print(df.isna().sum())

