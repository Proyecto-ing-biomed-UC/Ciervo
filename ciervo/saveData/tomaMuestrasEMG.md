# Modulo de Captura de Datos EMG (raspberry) con Docker y Python

## Descripción

Este modulo captura datos de señales EMG (Electromiografía) utilizando una interfaz gráfica (básica) desarrollada en Python con Tkinter, que permite iniciar, detener y guardar la grabación de datos. El proyecto utiliza contenedores Docker para gestionar los servicios de captura y almacenamiento de datos en una base de datos InfluxDB.

## Funcionalidades

- **Captura de datos EMG**: Recibe y almacena datos de señales EMG simuladas o reales.
- **Interfaz gráfica**: Permite iniciar y detener la captura de datos, así como guardarlos en formato CSV.
- **Automatización con Docker**: Gestión automatizada de servicios usando Docker Compose para desplegar los contenedores de captura de datos y almacenamiento.
- **Almacenamiento de datos**: Los datos capturados se almacenan en una base de datos InfluxDB y se pueden exportar a CSV.

## Requisitos

- **Docker** y **Docker Compose** instalados.
- **Python 3.10** o superior.
- Repositorio clonado con todos los archivos necesarios.

### Dependencias de Python

Estas dependencias se instalan automáticamente cuando se ejecuta el contenedor:

```plaintext
numpy
scipy
scikit-learn
seaborn
tqdm
paho-mqtt
influxdb-client
brainflow
tkinter
```
## Ejecución del Proyecto

### Paso 1: Iniciar la Grabación de Datos

1. **Abrir la Interfaz Gráfica (GUI):**
   - Ejecuta el archivo `gui_data_capture.py` para abrir la GUI de captura de datos:
     ```bash
     python3 ciervo/saveData/gui_data_capture.py
     ```

2. **Iniciar la Grabación:**
   - En la GUI, haz clic en "Iniciar Grabación". Esto lanzará los contenedores Docker y comenzará a capturar datos cuando todos los servicios estén listos.

### Paso 2: Detener la Grabación

1. **Detener la Grabación:**
   - En la GUI, haz clic en "Detener Grabación". Esto detendrá los contenedores Docker y finalizará la captura de datos.

### Paso 3: Guardar los Datos en un Archivo CSV

1. **Guardar los Datos:**
   - Después de detener la grabación, haz clic en "Guardar en CSV" para exportar los datos capturados en un archivo CSV.

### Paso 4: Verificar los Contenedores Docker

Si deseas verificar los contenedores Docker que están en ejecución, puedes utilizar el siguiente comando:

```bash
docker-compose ps
```