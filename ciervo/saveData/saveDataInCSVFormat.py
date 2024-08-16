import csv
import numpy as np
from influxdb_client import InfluxDBClient
from datetime import datetime
import ciervo.parameters as p
import os
# Configuración de la conexión
token = os.environ.get("INFLUXDB_TOKEN")
org = "Ciervo"
bucket = "Ciervo"


client = InfluxDBClient(url=p.URL_INFLUXDB, token=token, org=org)

# Query con un rango de una hora, se filtra por la medición EMG y se ordena por tiempo
query = f'''
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "EMG")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"])
'''

tables = client.query_api().query(query, org=org)

# Escribir los datos en un archivo CSV
with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Escribir encabezados
    writer.writerow([
        "unixtime_ms", "channel_0", "channel_30", "channel_1", "channel_2", "channel_3", 
        "channel_4", "channel_20_gyro", "channel_21_gyro", "channel_22_gyro"
    ])
    # Se deja en un formato en el cual hay 9 columnas (8 canales + timestamp))
    for table in tables:
        for record in table.records:
            
            timestamp = record.get_time()
            unix_time = int(timestamp.timestamp() * 1000)  # Convierte a milisegundos

            
            row = [
                unix_time,
                np.float16(record.values.get("channel_0", np.nan)),
                np.float16(record.values.get("channel_30", np.nan)),
                np.float16(record.values.get("channel_1", np.nan)),
                np.float16(record.values.get("channel_2", np.nan)),
                np.float16(record.values.get("channel_3", np.nan)),
                np.float16(record.values.get("channel_4", np.nan)),
                np.float16(record.values.get("channel_20", np.nan)),  # Giroscopio
                np.float16(record.values.get("channel_21", np.nan)),  # Giroscopio
                np.float16(record.values.get("channel_22", np.nan))   # Giroscopio
            ]
            writer.writerow(row)
