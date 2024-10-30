import paho.mqtt.client as mqtt
import json
from .models import Car

# MQTT Broker details (use mqtt.eclipseprojects.io for testing)
BROKER = "mqtt.eclipseprojects.io"
PORT = 1883
TOPIC = "sensor/data"

# Callback when a message is received from the broker
def receive_message(client, userdata, message):
    data = json.loads(message.payload.decode())

    try:
        # Retrieve the Car instance and update temperature
        car1 = Car.objects.get(id=data['car_id'])
        car1.temperature = data['car_temperature']
        car1.location_latitude = data['car_location_latitude']
        car1.location_longitude = data['car_location_longitude']
        car1.save()
        print(f"The temperature inside the car is: {data['car_temperature']}°C.")
    except Car.DoesNotExist:
        print(f"Car with ID {data['car_id']} does not exist.")
    except Exception as e:
        print(f"Error updating car temperature: {e}")

# Function to start the MQTT client in a non-blocking way
def start_mqtt_client():
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC)
    client.on_message = receive_message
    client.loop_start()  # Start the loop in a non-blocking way
