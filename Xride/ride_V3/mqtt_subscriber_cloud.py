import json
import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import os
from django.db import transaction
from .models import Car

# MQTT Broker details
MQTT_BROKER = "a1npc4fmgfecx6-ats.iot.us-east-2.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "car/+/xride/module/+/data"

# Temp file paths for storing certificate data
CA_CERT_PATH = "/tmp/ca_cert.pem"
CLIENT_CERT_PATH = "/tmp/client_cert.pem"
CLIENT_KEY_PATH = "/tmp/client_key.pem"

def write_cert_file(env_var, filename):
    """Writes certificate data from an environment variable to a file"""
    cert_content = os.environ.get(env_var)
    if not cert_content:
        raise ValueError(f"❌ Missing {env_var} environment variable")
    
    with open(filename, "w") as file:
        file.write(cert_content)

def on_connect(client, userdata, flags, rc):
    """Handles MQTT connection"""
    if rc == 0:
        print("✅ Successfully connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT Connection failed with error code {rc}")

def on_message(client, userdata, msg):
    """Handles incoming MQTT messages and updates the database"""
    try:
        data = json.loads(msg.payload.decode())
        print(f"📩 Received message: {data}")

        car_id = data.get("car-id") or data.get("car_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not car_id or latitude is None or longitude is None:
            print("⚠️ Missing required car data. Ignoring message.")
            return

        # Update car position in the database
        with transaction.atomic():
            car = Car.objects.select_for_update().get(id=car_id)
            car.latitude = latitude
            car.longitude = longitude
            car.save(update_fields=["latitude", "longitude"])
        
        print(f"✅ Updated car {car_id}: Lat={latitude}, Lon={longitude}")

    except Car.DoesNotExist:
        print(f"❌ Car with ID {car_id} not found in the database.")
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON message.")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def start_mqtt_client():
    """Initialize and run MQTT Client"""
    try:
        print("🔄 Initializing MQTT client...")

        # Write certificates to temporary files
        write_cert_file("CA_CERT", CA_CERT_PATH)
        write_cert_file("CLIENT_CERT", CLIENT_CERT_PATH)
        write_cert_file("CLIENT_KEY", CLIENT_KEY_PATH)

        # Create and configure MQTT client
        client = mqtt.Client()
        client.tls_set(
            ca_certs=CA_CERT_PATH,
            certfile=CLIENT_CERT_PATH,
            keyfile=CLIENT_KEY_PATH
        )
        client.on_connect = on_connect
        client.on_message = on_message

        print("🔗 Connecting to MQTT Broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        print("🚀 Starting MQTT loop...")
        client.loop_forever()

    except Exception as e:
        print(f"❌ Error initializing MQTT client: {e}")