import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client
from time import sleep
import random
import os; os.system('clear')


# Define the MQTT broker address and port
broker_address = "127.0.0.1"  # Replace with your broker's address
broker_port = 1883  # Default MQTT port is 1883
topic = "marker"
repetitions = 120

# Create a client instance
client = mqtt.Client(mqtt_client.CallbackAPIVersion.VERSION2)

# Connect to the broker
client.connect(broker_address, broker_port)

client.publish(topic, 0)

# cuenta regresiva
for i in range(4, 0, -1):
    os.system('clear')
    print(i)
    sleep(1)


for idx in range(repetitions):

    if idx % 2 == 0:
        message = 1
    else:
        message = 2 

    client.publish(topic, message)
    os.system('clear')
    if message == 1:
        print(f"Relaja!")
    else:
        print(f"Contrae!")
    sleep(2)


client.publish(topic, 0)

os.system('clear')
print("Fin del experimento")

# Disconnect from the broker
client.disconnect()

