import json
import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import threading
import time
from django.db import transaction
from .models import Car
import os
import redis
# MQTT Broker details

redis_client = redis.StrictRedis.from_url(
    "rediss://red-cjcsrendb61s739bj610:B59haYUZ3iFrOM9g0mzbWubr2ZfReoIc@oregon-redis.render.com:6379",
    ssl_cert_reqs=None  # Disables certificate validation
)
channel_layer = get_channel_layer()
MQTT_BROKER = "a1npc4fmgfecx6-ats.iot.us-east-2.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "car/+/xride/module/+/data"
Door_TOPIC = "car/+/xride/door"

# CA_CERT = r"D:\Grad\Testing\Certs\CA.pem"
# CLIENT_CERT = r"D:\Grad\Testing\Certs\client-certificate.pem.crt"
# CLIENT_KEY = r"D:\Grad\Testing\Certs\client-private.pem.key"


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

        redis_client.setex(f"car:{car_id}", 30, json.dumps(data))
        print(f"📡 Data cached for car {car_id} in Redis.")
        
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

def on_publish(client, userdata, mid):
    print(f"📤 Message Published with ID: {mid}")

def publish_message(topic, payload, type):
    """Publishes a message to an MQTT topic."""
    try:
        if type == "door":
            print("Initializing MQTT client for publishing...")
            client = mqtt.Client()
            # client.tls_set(CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

            client.tls_set(
                ca_certs=CA_CERT_PATH,
                certfile=CLIENT_CERT_PATH,
                keyfile=CLIENT_KEY_PATH
            )

            client.on_publish = on_publish
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            print(f"🔗 Connected to MQTT Broker for publishing. Publishing message...")
            client.publish(topic, json.dumps(payload), qos=1)
            time.sleep(6)

            print(f"📤 Published message to {topic}: {payload}")
            client.disconnect()
        if type == "status":
            print("Initializing MQTT client for publishing...")
            client = mqtt.Client()
            # client.tls_set(CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

            client.tls_set(
                ca_certs=CA_CERT_PATH,
                certfile=CLIENT_CERT_PATH,
                keyfile=CLIENT_KEY_PATH
            )

            client.on_publish = on_publish
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            print(f"🔗 Connected to MQTT Broker for publishing. Publishing message...")
            client.publish(topic, json.dumps(payload), qos=1)
            time.sleep(6)

            print(f"📤 Published message to {topic}: {payload}")
            client.disconnect()
    except Exception as e:
        print(f"❌ Error publishing message: {e}")

def update_database():
    """Function to update the database every 10 seconds from Redis."""
    while True:
        try:
            # Get all car IDs from Redis
            car_keys = redis_client.keys('car:*')

            for key in car_keys:
                car_id = key.decode().split(":")[1]
                car_data = json.loads(redis_client.get(key))

                if car_data:
                    latitude = car_data.get("Latitude")
                    longitude = car_data.get("Longitude")
                    speed = car_data.get("speed")
                    fuel = car_data.get("fuel")
                    engine_status = car_data.get("Engine")

                    if latitude is not None and longitude is not None:
                        with transaction.atomic():
                            car = Car.objects.select_for_update().get(id=car_id)
                            car.location_latitude = latitude
                            car.location_longitude = longitude
                            car.speed = speed
                            car.fuel_level = fuel
                            car.engine_status = engine_status
                            car.save(update_fields=["location_latitude", "location_longitude", "speed", "fuel_level", "engine_status"])
                            print(f"✅ Updated car {car_id} in database.")

            # Wait for 10 seconds before updating again
            time.sleep(10)

        except Exception as e:
            print(f"❌ Error updating database: {e}")
            time.sleep(10)


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
#         threading.Thread(target=update_database, daemon=True).start()
#         client.loop_forever()
#     except Exception as e:
#         print(f"Error initializing MQTT client: {e}")

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
