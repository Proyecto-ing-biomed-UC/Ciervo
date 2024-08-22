import paho.mqtt.client as mqtt
import numpy as np
import ciervo.parameters as p
from influxdb_client import InfluxDBClient, Point, WriteOptions
import os

# Configuración de la conexión a InfluxDB usando variables de entorno (PRUEBAS)
token = os.environ.get("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")  # Token de InfluxDB
org = os.environ.get("DOCKER_INFLUXDB_INIT_ORG", "default_org")  # Organización
bucket = os.environ.get("DOCKER_INFLUXDB_INIT_BUCKET", "default_bucket")  # Bucket

# Cliente de InfluxDB
client_influx = InfluxDBClient(url=p.URL_INFLUXDB, token=token, org=org)
write_api = client_influx.write_api(write_options=WriteOptions(batch_size=1))

def saveEMG(data):
    data = data.split(',')
    data = [float(x) for x in data]

    try:
        point = (
            Point("EMG")
            .field("channel_1", data[0])
            .field("channel_2", data[1])
            .field("channel_3", data[2])
            .field("channel_4", data[3])
            .field("channel_5", data[4])
            .field("channel_6", data[5])
            .field("channel_7", data[6])  
            .field("channel_8", data[7])  
            .field("channel_9", data[8])  
            .field("channel_10", data[9]) # Giroscopio X
            .field("channel_11", data[10]) # Giroscopio Y
            .field("channel_12", data[11]) # Giroscopio Z
            .field("channel_22", data[12]) # Time
        )
        write_api.write(bucket=bucket, record=point)
    except IndexError as e:
        print(f"Error: {e}. Data received: {data}")

def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker MQTT con código {rc}")
    client.subscribe("data")

def on_message(client, userdata, msg):
    data = np.frombuffer(msg.payload, dtype=p.PRECISION)
    print(f"Mensaje recibido: {data}")

    # Convertir el array de numpy en una cadena compatible con saveEMG
    data_str = ",".join(map(str, data))
    
    # Guardar los datos en InfluxDB usando saveEMG
    saveEMG(data_str)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Conectar al broker MQTT
    client.connect(p.BROKER_HOST, p.BROKER_PORT, 60)

    # Loop infinito de procesamiento de mensajes
    try:
        while True:
            client.loop(timeout=0.1)  # timeout=0.1 para que no bloquee el programa
    except KeyboardInterrupt:
        print("Desconectado del broker MQTT")
    finally:
        client.disconnect()

if __name__ == '__main__':
    main()
