# import paho.mqtt.client as mqtt
# import json
# from .models import Car
# import ssl

# BROKER = "a1npc4fmgfecx6-ats.iot.us-east-2.amazonaws.com"
# PORT = 8883
# TOPIC = "sensor/data"
# DOOR_TOPIC = "doorlock/state"
# CONFIRM_TOPIC = "confirmation"

# # Path to certificates
# ca_path = r"D:\Grad\Xride-App\Certs\root-CA.crt"
# cert_path = r"D:\Grad\Xride-App\Certs\Access_State.cert.pem.crt"
# key_path = r"D:\Grad\Xride-App\Certs\Access_State.private.key"

# # Callback when a message is received from the broker
# def Car_Sensor_Data_message(client, userdata, message):
#     data = json.loads(message.payload.decode())
#     try:
#         # Retrieve the Car instance and update temperature
#         car1 = Car.objects.get(id=data['car_id'])
#         car1.temperature = data['value']
#         car1.location_latitude = data['car_location_latitude']
#         car1.location_longitude = data['car_location_longitude']
#         car1.save()
#         print(f"The temperature inside car {data['car_id']} is: {data['value']}°C.")
#         print(f"The car location longitude is: {data['car_location_longitude']} and location latitude is: {data['car_location_latitude']}")
#         confirmation_message = {"confirmation": "Temperature data , location longitude and location latitude received successfully"}
#         client.publish(CONFIRM_TOPIC, json.dumps(confirmation_message))
#     except Car.DoesNotExist:
#         print(f"Car with ID {data['car_id']} does not exist.")
#     except Exception as e:
#         print(f"Error updating car temperature: {e}")

# def receive_message(client, userdata, message):
    
#     data = json.loads(message.payload.decode())
#     print(f"Received confirmation message: {data['confirmation']}")
#     client.loop_stop()

# def publish_car_door_state(car_id, door_state):
#     client = mqtt.Client()
#     client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
#     client.connect(BROKER, PORT, 60)
#     message = {
#         "car_id": car_id,
#         "door_state": door_state
#     }
#     client.publish(DOOR_TOPIC, json.dumps(message))
#     print(f"Published car {car_id} door state: {door_state}")
#     client.loop_start()  # Start the loop in a non-blocking way
#     client.on_message = receive_message

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected successfully!")
#         client.publish("MQTT/AWS/TESTTT", "Hello from device!")
#     else:
#         print("Connection failed with code", rc)

# def on_publish(client, userdata, mid):
#     print("Message published with mid:", mid)

# def start_mqtt_client():
#     # Setup TLS
#     client = mqtt.Client()
#     client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
#     client.connect(BROKER, PORT, 60)
#     client.subscribe(TOPIC)
#     client.subscribe(CONFIRM_TOPIC)

#     # client.on_connect = on_connect
#     # client.on_publish = 
#     client.loop_start()

