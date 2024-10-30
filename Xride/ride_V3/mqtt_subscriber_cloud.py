import paho.mqtt.client as mqtt
import json
from .models import Car

# MQTT Broker details (use mqtt.eclipseprojects.io for testing)
BROKER = "mqtt.eclipseprojects.io"
PORT = 1883
TOPIC = "sensor/data"
CONFIRM_TOPIC = "confirmation"

# Callback when a message is received from the broker
def receive_message(client, userdata, message):
    data = json.loads(message.payload.decode())

    try:
        # Retrieve the Car instance and update temperature
        car1 = Car.objects.get(id=data['car_id'])
        car1.temperature = data['value']
        car1.location_latitude = data['car_location_latitude']
        car1.location_longitude = data['car_location_longitude']
        car1.save()
        print(f"The temperature inside car {data['car_id']} is: {data['value']}°C.")
        print(f"The car location longitude is: {data['car_location_longitude']} and location latitude is: {data['car_location_latitude']}")
        confirmation_message = {"confirmation": "Temperature data , location longitude and location latitude received successfully"}
        client.publish(CONFIRM_TOPIC, json.dumps(confirmation_message))
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
