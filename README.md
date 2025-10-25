# Parte 1

## Instalación de dependencias
```bash
pip install -r requirements.txt
```
# Fase 1: Data Ingestion (Generación y Organización de Datos)

## 📋 Descripción general

En esta primera fase se configuró la base del *Data Lake local* y se ejecutó el proceso de generación automática de transacciones.  
El objetivo fue establecer una estructura organizada para la ingesta continua de datos y preparar el entorno para las siguientes fases del pipeline ETL.

El archivo `main.py` se encarga de generar archivos CSV con transacciones simuladas cada 60 segundos dentro de la carpeta `transactions/`.

Durante esta fase:
- Se ejecutó `main.py` para verificar la creación automática de los archivos CSV.

## Ejecución
```bash
python3 main.py
```

- Se verificó que los archivos CSV fueran generados correctamente por main.py y que su estructura (columnas y formato) fuera consistente entre los distintos archivos.

## Fase 2: Inspección de Transacciones

### 📋 Descripción general

El script `inspect_transactions.py` permite analizar los archivos CSV generados en la carpeta `transactions/`.  
Este script realiza validaciones básicas, como verificar la consistencia de las columnas y detectar posibles errores en los datos.

### Ejecución
```bash
python3 inspect_transactions.py
```

- El script genera un reporte con los resultados de la inspección, indicando si los archivos cumplen con los estándares definidos.



