"""
Script para inspeccionar las columnas de un archivo CSV limpio en ./processed.
Permite validar los datos disponibles antes de diseñar el modelo dimensional y crear las tablas en PostgreSQL.
Uso recomendado: Ejecutar antes de definir el esquema en SQLAlchemy.
"""

import pandas as pd
from pathlib import Path


def inspeccionar_csv_procesado():
    processed_folder = Path("../processed")  # Ruta relativa desde scripts/
    csv_files = sorted(processed_folder.glob("*.csv"))
    if not csv_files:
        print("No se encontraron archivos en ./processed")
        return

    latest_file = csv_files[-1]
    print(f"Archivo analizado: {latest_file.name}")
    df = pd.read_csv(latest_file)
    print("\nColumnas disponibles:")
    print(df.columns.tolist())
    print("\nPrimeras filas:")
    print(df.head())
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nValores nulos por columna:")
    print(df.isna().sum())

if __name__ == "__main__":
    inspeccionar_csv_procesado()
