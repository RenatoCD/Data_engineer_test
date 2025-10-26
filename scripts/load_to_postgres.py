"""
Script para cargar los datos limpios de ./processed en las tablas del Data Warehouse en PostgreSQL.
Requiere que las tablas ya hayan sido creadas con create_tables.py.
"""

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime

# Importar los modelos
try:
    from create_tables import Base, DimUser, DimMerchant, DimPaymentMethod, DimTime, FactTransaction
except ImportError as e:
    print(f"Error importando modelos: {e}")
    exit(1)

# Configuración de conexión
DATABASE_URL = "postgresql+psycopg2://postgres:xxx@localhost:5432/db_fintech"
try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
except Exception as e:
    print(f"Error conectando a la base de datos: {e}")
    exit(1)

# Leer el archivo CSV limpio más reciente
def cargar_datos():
    try:
        processed_folder = Path("../processed")
        csv_files = sorted(processed_folder.glob("*.csv"))
        if not csv_files:
            print("No se encontraron archivos en ./processed")
            return
        latest_file = csv_files[-1]
        print(f"Cargando datos desde: {latest_file.name}")
        df = pd.read_csv(latest_file)
    except Exception as e:
        print(f"Error leyendo el archivo CSV: {e}")
        return

    # Diccionarios para evitar duplicados en dimensiones
    usuarios = {}
    merchants = {}
    payment_methods = {}
    times = {}

    try:
        for _, row in df.iterrows():
            # DimUser
            user_id = int(row['user_id'])
            if user_id not in usuarios:
                usuario = DimUser(
                    user_id=user_id,
                    country=row.get('country'),
                    device_type=row.get('device_type'),
                    ip_address=row.get('ip_address'),
                    user_agent=row.get('user_agent')
                )
                session.merge(usuario)
                usuarios[user_id] = usuario

            # DimMerchant
            merchant_id = int(row['merchant_id'])
            if merchant_id not in merchants:
                merchant = DimMerchant(
                    merchant_id=merchant_id,
                    category=row.get('category'),
                    country=row.get('country')
                )
                session.merge(merchant)
                merchants[merchant_id] = merchant

            # DimPaymentMethod
            pm_key = (row.get('payment_method'), row.get('payment_provider'))
            if pm_key not in payment_methods:
                payment_method = DimPaymentMethod(
                    payment_method=row.get('payment_method'),
                    payment_provider=row.get('payment_provider')
                )
                session.add(payment_method)
                session.flush()  # Para obtener el payment_method_id
                payment_methods[pm_key] = payment_method.payment_method_id
            payment_method_id = payment_methods[pm_key]

            # DimTime
            timestamp_str = row.get('timestamp')
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                timestamp = None
            time_key = (timestamp_str, row.get('settlement_date'))
            if time_key not in times:
                if timestamp:
                    time = DimTime(
                        timestamp=timestamp,
                        year=timestamp.year,
                        month=timestamp.month,
                        day=timestamp.day,
                        hour=timestamp.hour,
                        minute=timestamp.minute,
                        second=timestamp.second,
                        settlement_date=row.get('settlement_date')
                    )
                    session.add(time)
                    session.flush()
                    times[time_key] = time.time_id
                else:
                    times[time_key] = None
            time_id = times[time_key]

            # FactTransaction
            fact = FactTransaction(
                transaction_id=row['transaction_id'],
                user_id=user_id,
                merchant_id=merchant_id,
                payment_method_id=payment_method_id,
                time_id=time_id,
                amount=row.get('amount'),
                currency=row.get('currency'),
                status=row.get('status'),
                response_code=row.get('response_code'),
                response_message=row.get('response_message'),
                fee_percentage=row.get('fee_percentage'),
                transaction_fee=row.get('transaction_fee'),
                net_amount=row.get('net_amount'),
                attempt_number=row.get('attempt_number'),
                processing_time_ms=row.get('processing_time_ms'),
                three_ds_verified=row.get('three_ds_verified'),
                installments=row.get('installments'),
                is_international=row.get('is_international')
            )
            session.merge(fact)

        session.commit()
        print("Datos cargados correctamente.")
    except Exception as e:
        session.rollback()
        print(f"Error al cargar los datos: {e}")

if __name__ == "__main__":
    cargar_datos()
