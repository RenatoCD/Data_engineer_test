"""
Main ETL Pipeline for Transaction Processing

This script runs continuously, generating fake transactions every minute
and processing them through a data pipeline.

TODO: Complete the following functions:
1. clean_data() - Clean and validate the raw transaction data
2. detect_suspicious_transactions() - Identify potentially fraudulent transactions
"""

import time
import pandas as pd
from datetime import datetime
from pathlib import Path
from scripts.generate_transactions import generate_transactions


# Configuration
TRANSACTIONS_FOLDER = Path("./transactions")
PROCESSED_FOLDER = Path("./processed")
SUSPICIOUS_FOLDER = Path("./suspicious")
INTERVAL_SECONDS = 60  # Generate transactions every 1 minute
TRANSACTIONS_PER_BATCH = 100  # Number of transactions to generate each time


def setup_folders():
    """Create necessary folders if they don't exist"""
    TRANSACTIONS_FOLDER.mkdir(exist_ok=True)
    PROCESSED_FOLDER.mkdir(exist_ok=True)
    SUSPICIOUS_FOLDER.mkdir(exist_ok=True)
    print(f"Folders initialized:")
    print(f"  - Data Lake: {TRANSACTIONS_FOLDER}")
    print(f"  - Processed: {PROCESSED_FOLDER}")
    print(f"  - Suspicious: {SUSPICIOUS_FOLDER}")


def generate_batch():
    """Generate a batch of fake transactions and save to data lake"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = TRANSACTIONS_FOLDER / f"transactions_{timestamp}.csv"

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generating {TRANSACTIONS_PER_BATCH} transactions...")
    df = generate_transactions(TRANSACTIONS_PER_BATCH)
    df.to_csv(filename, index=False)
    print(f"Saved to: {filename}")

    return filename


def clean_data(df):
    """
    TODO: Implement data cleaning logic

    Clean and validate the transaction data. Consider:
    - Handling missing values
    - Removing duplicates
    - Data type validation
    - Standardizing formats
    - Handling outliers

    Args:
        df (pd.DataFrame): Raw transaction data

    Returns:
        pd.DataFrame: Cleaned transaction data
    """
    # YOUR CODE HERE
    # Validación de DataFrame vacío
    if df.empty:
        raise ValueError("El archivo CSV está vacío. No se puede procesar.")

    df_clean = df.copy()

    # Si el DataFrame tiene una sola columna, probablemente no se leyó correctamente
    if len(df_clean.columns) == 1:
        df_clean = pd.read_csv(df_clean, delimiter=';')

    # Definir columnas críticas
    columnas_criticas = [
        'transaction_id', 'user_id', 'merchant_id', 'amount', 'currency',
        'status', 'timestamp', 'payment_method', 'country'
    ]

    # Validar que existan las columnas críticas
    faltantes = [col for col in columnas_criticas if col not in df_clean.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas críticas en el DataFrame: {faltantes}")

    # Filtrar solo las columnas críticas
    df_clean = df_clean[columnas_criticas].copy()

    # Eliminar filas con valores nulos en columnas críticas
    df_clean.dropna(subset=columnas_criticas, inplace=True)

    # Eliminar duplicados considerando solo columnas críticas
    df_clean.drop_duplicates(subset=columnas_criticas, inplace=True)

    # Estandarizar y validar tipos en columnas tipo texto
    for col in ['transaction_id', 'user_id', 'merchant_id', 'currency', 'status', 'payment_method', 'country']:
        df_clean[col] = df_clean[col].fillna('').astype(str).str.upper().str.strip()

    # Convertir columna 'amount' a numérico
    df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')

    # Convertir columna 'timestamp' a datetime
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], errors='coerce')
    df_clean.dropna(subset=['timestamp'], inplace=True)

    # Manejo de outliers en 'amount' usando IQR
    q1 = df_clean['amount'].quantile(0.25)
    q3 = df_clean['amount'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    df_clean = df_clean[(df_clean['amount'] >= lower_bound) & (df_clean['amount'] <= upper_bound)]

    return df_clean
    #raise NotImplementedError("clean_data() function needs to be implemented")


def detect_suspicious_transactions(df):
    """
    TODO: Implement fraud detection logic

    Identify suspicious transactions based on various criteria. Consider:
    - Unusually high amounts
    - Multiple failed attempts
    - High-risk countries or merchants
    - Unusual transaction patterns
    - Time-based anomalies
    - Multiple transactions in short time

    Args:
        df (pd.DataFrame): Cleaned transaction data

    Returns:
        tuple: (normal_df, suspicious_df) - DataFrames split by suspicion status
    """
    # YOUR CODE HERE
    # Inicializar columna de sospecha
    df = df.copy()
    df['is_suspicious'] = False

    # 1. Montos inusualmente altos (mayores al percentil 99)
    high_amount_threshold = df['amount'].quantile(0.99)
    df.loc[df['amount'] > high_amount_threshold, 'is_suspicious'] = True

    # 2. Múltiples intentos fallidos del mismo usuario (status == 'declined')
    if 'user_id' in df.columns and 'status' in df.columns:
        failed_attempts = df[df['status'].str.lower() == 'declined'].groupby('user_id').size()
        suspicious_users = failed_attempts[failed_attempts >= 3].index
        df.loc[df['user_id'].isin(suspicious_users), 'is_suspicious'] = True

    # 3. Flaggear transacciones declined con códigos de seguridad (ejemplo: security_code == 'FRAUD' o 'BLOCKED')
    if 'security_code' in df.columns:
        df.loc[df['security_code'].isin(['FRAUD', 'BLOCKED']), 'is_suspicious'] = True

    # 4. Detectar patrones anómalos: múltiples transacciones en menos de 1 minuto por usuario
    if 'user_id' in df.columns:
        df_sorted = df.sort_values(['user_id', 'timestamp'])
        df_sorted['time_diff'] = df_sorted.groupby('user_id')['timestamp'].diff().dt.total_seconds()
        rapid_tx = df_sorted[(df_sorted['time_diff'] <= 60) & (df_sorted['time_diff'] > 0)]
        df.loc[rapid_tx.index, 'is_suspicious'] = True

    # 5. Transacciones internacionales de alto riesgo (país distinto al merchant y monto alto)
    if 'merchant_country' in df.columns:
        intl_risk = (df['country'] != df['merchant_country']) & (df['amount'] > high_amount_threshold)
        df.loc[intl_risk, 'is_suspicious'] = True

    # 6. Otros patrones: transacciones en horarios inusuales (ejemplo: entre 00:00 y 05:00)
    df['hour'] = df['timestamp'].dt.hour
    df.loc[df['hour'].between(0, 5), 'is_suspicious'] = True

    # Separar DataFrames
    suspicious_df = df[df['is_suspicious']].drop(columns=['is_suspicious', 'hour'], errors='ignore')
    normal_df = df[~df['is_suspicious']].drop(columns=['is_suspicious', 'hour'], errors='ignore')

    #raise NotImplementedError("detect_suspicious_transactions() function needs to be implemented")
    return normal_df, suspicious_df


def process_batch(raw_file):
    """
    Process a batch of transactions through the ETL pipeline

    Args:
        raw_file (Path): Path to the raw transaction CSV file
    """
    try:
        # Read raw data from data lake
        print(f"Reading data from: {raw_file}")
        df_raw = pd.read_csv(raw_file)
        print(f"Loaded {len(df_raw)} transactions")

        # Step 1: Clean the data
        print("Cleaning data...")
        df_clean = clean_data(df_raw)
        print(f"Cleaned {len(df_clean)} transactions")

        # Step 2: Detect suspicious transactions
        print("Detecting suspicious transactions...")
        df_normal, df_suspicious = detect_suspicious_transactions(df_clean)
        print(f"Found {len(df_suspicious)} suspicious transactions")
        print(f"Found {len(df_normal)} normal transactions")

        # Save processed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if len(df_normal) > 0:
            normal_file = PROCESSED_FOLDER / f"processed_{timestamp}.csv"
            df_normal.to_csv(normal_file, index=False)
            print(f"Saved normal transactions to: {normal_file}")

        if len(df_suspicious) > 0:
            suspicious_file = SUSPICIOUS_FOLDER / f"suspicious_{timestamp}.csv"
            df_suspicious.to_csv(suspicious_file, index=False)
            print(f"WARNING: Saved suspicious transactions to: {suspicious_file}")

        print(f"Batch processing completed successfully")

    except NotImplementedError as e:
        print(f"WARNING: Skipping processing: {e}")
    except Exception as e:
        print(f"ERROR: Error processing batch: {e}")


def main():
    """Main loop - generates and processes transactions every minute"""
    print("="*60)
    print("Transaction Processing Pipeline")
    print("="*60)

    setup_folders()

    print(f"\nStarting continuous processing (every {INTERVAL_SECONDS} seconds)")
    print("Press Ctrl+C to stop\n")

    batch_count = 0

    try:
        while True:
            batch_count += 1
            print(f"\n{'='*60}")
            print(f"BATCH #{batch_count}")
            print(f"{'='*60}")

            # Generate new transactions
            raw_file = generate_batch()

            # Process the batch
            process_batch(raw_file)

            # Wait for next interval
            print(f"\nWaiting {INTERVAL_SECONDS} seconds until next batch...")
            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\nPipeline stopped by user")
        print(f"Total batches processed: {batch_count}")


if __name__ == "__main__":
    main()


