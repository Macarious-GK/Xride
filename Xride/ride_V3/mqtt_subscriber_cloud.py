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
latest_car_status = {}
channel_layer = get_channel_layer()
MQTT_BROKER = "a1npc4fmgfecx6-ats.iot.us-east-2.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "car/+/xride/module/+/data"
Door_TOPIC = "car/+/xride/door"

# CA_CERT = r"D:\Grad\Testing\Certs\CA.pem"
# CLIENT_CERT = r"D:\Grad\Testing\Certs\client-certificate.pem.crt"
# CLIENT_KEY = r"D:\Grad\Testing\Certs\client-private.pem.key"

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
    """Callback when MQTT connects"""
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT Connection failed with error code {rc}")


def on_message(client, userdata, msg):
    """Handles incoming MQTT messages by updating the database, 
    storing the latest status in-memory, and pushing updates to WebSockets."""
    try:
        data = json.loads(msg.payload.decode())
        print(f"📩 Received message: {data}")

        # Extract car details
        car_id = data.get("car-id") or data.get("car_id")
        latitude = data.get("Latitude")
        longitude = data.get("Longitude")
        module = data.get("module")

        if not car_id:
            print("⚠️ Missing car_id in received message. Ignoring.")
            return

        # Update in-memory store
        latest_car_status[car_id] = data
        print("outatomic")
        # Update the database
        if latitude is not None and longitude is not None:
            print("in atomic")
            with transaction.atomic():
                car = Car.objects.select_for_update().get(id=car_id)
                car.location_latitude = latitude
                car.location_longitude = longitude
                car.speed = data.get("speed")
                car.fuel_level = data.get("fuel")
                car.engine_status = data.get("Engine")
        
                car.save(update_fields=["location_longitude", "location_latitude", "speed", "fuel_level", "engine_status"])
            
            print(f"✅ Updated car {car_id}: Lat={latitude}, Lon={longitude}")

        # Send update to WebSockets
        async_to_sync(channel_layer.group_send)(
            "car_status_group",
            {
                "type": "car_update_event",
                "data": data,
            }
        )

    except Car.DoesNotExist:
        print(f"❌ Car with ID {car_id} not found in the database.")
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON message.")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def publish_message(topic, payload):
    """Publishes a message to an MQTT topic."""
    try:
        print("Initializing MQTT client for publishing...")
        client = mqtt.Client()
        client.tls_set(
            ca_certs=CA_CERT_PATH,
            certfile=CLIENT_CERT_PATH,
            keyfile=CLIENT_KEY_PATH
        )
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"🔗 Connected to MQTT Broker for publishing. Publishing message...")
        client.publish(topic, json.dumps(payload))
        print(f"📤 Published message to {topic}: {payload}")
        client.disconnect()
    except Exception as e:
        print(f"❌ Error publishing message: {e}")


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


# def on_message(client, userdata, msg):
#     """Handles incoming MQTT messages and updates in-memory store + pushes to WebSockets"""
#     data = json.loads(msg.payload.decode())
#     if data.get("car-id"):
#         car_id = data.get("car-id")
#     if data.get("car_id"):
#         car_id = data.get("car_id") 
#     module = data.get("module")

#     # print("Data from MQTT: ",data)
#     if not car_id:
#         print("⚠️ Missing car-id in received message. Ignoring.")
#         return
#     latest_car_status[car_id] = data

#     # Send update to WebSockets
#     async_to_sync(channel_layer.group_send)(
#         "car_status_group",
#         {
#             "type": "car_update_event",
#             "data": data,
#         }
#     )
#     # print("Data sent to WebSocket via group_send")
#     # print("after",data)
#     # car  = car.objects.get(id=car_id)
#     # car.latitude = data.get("latitude")
#     # car.longitude = data.get("longitude")   
#     # car.save(updata_fields=['latitude', 'longitude'])

# def start_mqtt_client():
#     """Initialize and run MQTT Client"""
#     try:
#         print("Initializing MQTT client...")
#         client = mqtt.Client()
#         client.tls_set(CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY)
#         client.on_connect = on_connect
#         client.on_message = on_message
#         client.connect(MQTT_BROKER, MQTT_PORT, 60)

#         # Start background database update task
#         # threading.Thread(target=update_database, daemon=True).start()

#         client.loop_forever()
#     except Exception as e:
#         print(f"Error initializing MQTT client: {e}")