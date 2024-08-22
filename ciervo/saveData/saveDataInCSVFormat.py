import csv
import numpy as np
from influxdb_client import InfluxDBClient
import ciervo.parameters as p

# Configuración de la conexión

client = InfluxDBClient(url=p.URL_INFLUXDB, token=p.INFLUXDB_TOKEN, org=p.INFLUXDB_ORG)

# Query con un rango de una hora, se filtra por la medición EMG y se ordena por tiempo
query = f'''
from(bucket: "{p.INFLUXDB_BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "EMG")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"])
'''

tables = client.query_api().query(query, org=p.INFLUXDB_ORG)

# Escribir los datos en un archivo CSV
with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Escribir encabezados
    writer.writerow([
        "unixtime_ms", "channel_1", "channel_2", "channel_3", "channel_4", "channel_5", 
        "channel_6", "channel_7", "channel_8", "channel_9", "channel_10_gyro", "channel_11_gyro", "channel_12_gyro", "channel_22_time"
    ])
    # Se deja en un formato en el cual hay 13 columnas ( 12 canales + timestamp))
    for table in tables:
        for record in table.records:
            
            timestamp = record.get_time()
            unix_time = int(timestamp.timestamp() * 1000)  # Convierte a milisegundos

            
            row = [
                unix_time,
                np.float16(record.values.get("channel_1", np.nan)),
                np.float16(record.values.get("channel_2", np.nan)),
                np.float16(record.values.get("channel_3", np.nan)),
                np.float16(record.values.get("channel_4", np.nan)),
                np.float16(record.values.get("channel_5", np.nan)),
                np.float16(record.values.get("channel_6", np.nan)),
                np.float16(record.values.get("channel_7", np.nan)),  
                np.float16(record.values.get("channel_8", np.nan)),  
                np.float16(record.values.get("channel_9", np.nan)),
                np.float16(record.values.get("channel_10", np.nan)),  # Giroscopio X
                np.float16(record.values.get("channel_11", np.nan)),  # Giroscopio Y
                np.float16(record.values.get("channel_12", np.nan)),   # Giroscopio Z
                np.float16(record.values.get("channel_22", np.nan))   # Time
            ]
            writer.writerow(row)
