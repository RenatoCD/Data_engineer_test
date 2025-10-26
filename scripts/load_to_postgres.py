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
DATABASE_URL = "postgresql+psycopg2://postgres:admin123@localhost:5432/db_fintech"
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
        # Reemplazar iterrows() por itertuples() para mejor performance
        for row in df.itertuples(index=False):
            # Intentar convertir timestamp
            timestamp_str = getattr(row, 'timestamp', None)
            try:
                timestamp = datetime.strptime(str(timestamp_str), "%Y-%m-%d %H:%M:%S")
            except Exception:
                print(f"Fila ignorada por timestamp inválido: {row.transaction_id}")
                continue  # Ignorar la fila completa

            # DimUser
            user_id = int(row.user_id)
            if user_id not in usuarios:
                usuario = DimUser(
                    user_id=user_id,
                    country=getattr(row, 'country', None)
                )
                session.merge(usuario)
                usuarios[user_id] = usuario

            # DimMerchant
            merchant_id = int(row.merchant_id)
            if merchant_id not in merchants:
                merchant = DimMerchant(
                    merchant_id=merchant_id,
                    country=getattr(row, 'country', None)
                )
                session.merge(merchant)
                merchants[merchant_id] = merchant

            # DimPaymentMethod
            pm_key = getattr(row, 'payment_method', None)
            if pm_key not in payment_methods:
                payment_method = DimPaymentMethod(
                    payment_method=getattr(row, 'payment_method', None)
                )
                session.add(payment_method)
                session.flush()  # Para obtener el payment_method_id
                payment_methods[pm_key] = payment_method.payment_method_id
            payment_method_id = payment_methods[pm_key]

            # DimTime
            settlement_date = str(timestamp.date())
            time_key = (timestamp_str, settlement_date)
            if time_key not in times:
                time = DimTime(
                    timestamp=timestamp,
                    year=timestamp.year,
                    month=timestamp.month,
                    day=timestamp.day,
                    hour=timestamp.hour,
                    minute=timestamp.minute,
                    second=timestamp.second,
                    settlement_date=settlement_date
                )
                session.add(time)
                session.flush()
                times[time_key] = time.time_id
            time_id = times[time_key]

            # FactTransaction
            fact = FactTransaction(
                transaction_id=row.transaction_id,
                user_id=user_id,
                merchant_id=merchant_id,
                payment_method_id=payment_method_id,
                time_id=time_id,
                amount=getattr(row, 'amount', None),
                currency=getattr(row, 'currency', None),
                status=getattr(row, 'status', None),
                response_message=getattr(row, 'response_message', None)
            )
            session.merge(fact)

        session.commit()
        print("Datos cargados correctamente.")
    except Exception as e:
        session.rollback()
        print(f"Error al cargar los datos: {e}")

if __name__ == "__main__":
    cargar_datos()
