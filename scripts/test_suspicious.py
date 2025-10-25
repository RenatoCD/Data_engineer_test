import sys
from pathlib import Path
import pandas as pd

# Agrega la raíz del proyecto al path para importar main.py
directory_root = Path(__file__).resolve().parent.parent
sys.path.append(str(directory_root))

from main import clean_data, detect_suspicious_transactions

# Carpeta donde main.py genera los CSV
transactions_folder = directory_root / "transactions"

# Selecciona el archivo más reciente de transacciones
csv_files = sorted(transactions_folder.glob("transactions_*.csv"), reverse=True)
if not csv_files:
    print("No se encontraron archivos de transacciones para probar.")
    exit(1)

latest_file = csv_files[0]
print(f"Probando con archivo: {latest_file}")

# Lee y limpia los datos
df_raw = pd.read_csv(latest_file)
df_clean = clean_data(df_raw)

# Detecta transacciones sospechosas
normal_df, suspicious_df = detect_suspicious_transactions(df_clean)

print("\n--- RESULTADOS DE LA DETECCIÓN DE FRAUDE ---")
print(f"Transacciones normales: {len(normal_df)}")
print(f"Transacciones sospechosas: {len(suspicious_df)}")

if not suspicious_df.empty:
    print("\nEjemplo de transacciones sospechosas:")
    print(suspicious_df.head())
else:
    print("No se detectaron transacciones sospechosas.")
