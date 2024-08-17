import numpy as np

# MQTT params
# BROKER_HOST = '127.0.0.1'
BROKER_HOST = '100.90.57.1'
URL_INFLUXDB = 'http://100.90.57.1:8086'
BROKER_PORT = 1883
PRECISION = np.float64  
CHANNELS = [0, 30, 1, 2, 3, 4, 20, 21, 22]  # Synthetic Stream  #20, 21, 22 -> gyroscopio
NUM_CHANNELS  = len(CHANNELS)
SAMPLE_RATE = 250
TOPIC = 'data'
TOKEN = ''
INFLUXDB_TOKEN= "holas"
INFLUXDB_ORG = "Ciervo"
INFLUXDB_BUCKET = "Ciervo"