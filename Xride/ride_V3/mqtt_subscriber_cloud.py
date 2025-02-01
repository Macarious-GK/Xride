import json
import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import threading
import time
from django.db import transaction
from .models import Car
import os

# MQTT Broker details
MQTT_BROKER = "a1npc4fmgfecx6-ats.iot.us-east-2.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "car/+/xride/module/+/data"

# TLS/SSL Certificate Paths
CA_CERT = os.environ.get("CA_CERT")
CLIENT_CERT = os.environ.get("CLIENT_CERT")
CLIENT_KEY = os.environ.get("CLIENT_KEY")


def on_connect(client, userdata, flags, rc):
    """Callback when MQTT connects"""
    print(f"Connected with result code {rc}")
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT Connection failed with error code {rc}")

def on_message(client, userdata, msg):
    """Handles incoming MQTT messages and updates in-memory store + pushes to WebSockets"""
    data = json.loads(msg.payload.decode())
    if data.get("car-id"):
        car_id = data.get("car-id")
    if data.get("car_id"):
        car_id = data.get("car_id") 
    module = data.get("module")

    print(data)
    if not car_id:
        print("⚠️ Missing car-id in received message. Ignoring.")
        return
    car  = car.objects.get(id=car_id)
    car.latitude = data.get("latitude")
    car.longitude = data.get("longitude")   
    car.save(updata_fields=['latitude', 'longitude'])

 
def start_mqtt_client():
    """Initialize and run MQTT Client"""
    try:
        print("Initializing MQTT client...")
        client = mqtt.Client()
        print("Setting TLS certificates...")
        client.tls_set(CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY)
        print("Setting callbacks...")
        client.on_connect = on_connect
        client.on_message = on_message
        print("Connecting to MQTT Broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("Starting MQTT loop...")
        # Start background database update task
        # threading.Thread(target=update_database, daemon=True).start()

        client.loop_forever()
    except Exception as e:
        print(f"Error initializing MQTT client: {e}")
