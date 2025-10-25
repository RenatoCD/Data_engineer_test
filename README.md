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


# Parte 2. 
Decisión sobre la limpieza de datos
Durante la fase de limpieza de datos, se evaluaron dos enfoques:

## Limpieza de todas las columnas:

 Ventaja: Garantiza máxima calidad y consistencia en todos los campos.
Desventaja: Puede eliminar una gran cantidad de registros por valores faltantes o inconsistentes en columnas poco relevantes, reduciendo el volumen de datos útil para análisis y detección de fraude.

Datos totales después de limpieza:

* Cantidad de filas originales: 100
* Cantidad de filas después de limpieza: 54


## Limpieza solo de columnas críticas:

Ventaja: Preserva más registros, enfocándose en los campos esenciales para el análisis y la detección de transacciones sospechosas.
Desventaja: Puede dejar inconsistencias menores en columnas no críticas, pero no afecta la calidad del análisis principal.

Decisión tomada:
Se optó por limpiar únicamente las columnas críticas para el proceso de análisis y detección de fraude:

* transaction_id
* user_id
* merchant_id
* amount
* currency
* status
* timestamp
* payment_method
* country

Esta decisión permite mantener la mayor cantidad de datos posible, asegurando la calidad en los campos relevantes y facilitando la detección de patrones sospechosos sin sacrificar volumen de información.

## Justificación numérica:

Haciendo limpieza de columnas críticas los resultados son mejores: 
* Cantidad de filas originales: 100
* Cantidad de filas después de limpieza: 93


