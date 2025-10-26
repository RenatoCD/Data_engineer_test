"""
Script para crear las tablas del Data Warehouse en PostgreSQL usando SQLAlchemy.
El modelo dimensional se basa en las columnas reales del CSV limpio inspeccionado.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Dimensión Usuarios
class DimUser(Base):
    __tablename__ = 'dim_users'
    user_id = Column(Integer, primary_key=True)
    country = Column(String)

# Dimensión Comercios
class DimMerchant(Base):
    __tablename__ = 'dim_merchants'
    merchant_id = Column(Integer, primary_key=True)
    country = Column(String)

# Dimensión Métodos de Pago
class DimPaymentMethod(Base):
    __tablename__ = 'dim_payment_methods'
    payment_method_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method = Column(String)
    payment_provider = Column(String)

# Dimensión Temporal
class DimTime(Base):
    __tablename__ = 'dim_time'
    time_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    hour = Column(Integer)
    minute = Column(Integer)
    second = Column(Integer)

# Tabla de Hechos
class FactTransaction(Base):
    __tablename__ = 'fact_transactions'
    transaction_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('dim_users.user_id'))
    merchant_id = Column(Integer, ForeignKey('dim_merchants.merchant_id'))
    payment_method_id = Column(Integer, ForeignKey('dim_payment_methods.payment_method_id'))
    time_id = Column(Integer, ForeignKey('dim_time.time_id'))
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    response_code = Column(String)
    response_message = Column(String)
    fee_percentage = Column(Float)
    transaction_fee = Column(Float)
    net_amount = Column(Float)
    attempt_number = Column(Integer)
    processing_time_ms = Column(Integer)
    three_ds_verified = Column(String)
    installments = Column(Integer)
    is_international = Column(Boolean)

# Crear engine y las tablas
if __name__ == "__main__":
    # Cadena de conexión 
    engine = create_engine("postgresql+psycopg2://postgres:xxxx@localhost:5432/db_fintech")
    Base.metadata.create_all(engine)
    print("Tablas creadas correctamente.")

"""
Justificación del esquema:

- Las dimensiones se diseñaron para capturar los atributos principales de usuarios, comercios, métodos de pago y tiempo, usando las columnas relevantes del CSV limpio.
- La tabla de hechos `fact_transactions` almacena las transacciones y referencia las dimensiones mediante claves foráneas, además de incluir métricas y atributos transaccionales (monto, estado, fees, intentos, internacionalidad, etc).
- Se priorizaron columnas que aportan valor analítico y permiten responder preguntas de negocio (por usuario, comercio, método, tiempo, país, categoría, etc).
- Las columnas que son identificadores o atributos repetidos se ubicaron en dimensiones para evitar redundancia y facilitar el análisis.
- El modelo sigue el esquema estrella (star schema) recomendado para análisis OLAP y BI.
"""