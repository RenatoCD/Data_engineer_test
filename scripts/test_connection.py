from sqlalchemy import create_engine

# Modifica la cadena de conexión con tus credenciales
engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/db_fintech")

try:
    with engine.connect() as conn:
        print("Conexión exitosa a PostgreSQL")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
