# consumers.py
import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Car
from asgiref.sync import sync_to_async
# This dictionary will hold the latest car statuses

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "test_room"

        # Join room group
        print ("we are her")
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print('disconnext')
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        event = {
                'type': 'send_message',
                'message': message
            }
        await self.channel_layer.group_send(self.room_group_name,event)

    # Receive message from room group
    async def send_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}))

import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

# Thread-safe shared storage for car status
latest_car_status = {}
status_lock = asyncio.Lock()

class CarStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'car_status_group'
        
        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

        # Start an async loop to push updates periodically
        self.update_task = asyncio.create_task(self.send_car_updates())

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Cancel the update task when disconnecting
        if hasattr(self, "update_task"):
            self.update_task.cancel()

    async def get_car_data_from_dict(self):
        """Fetch the latest car data from the in-memory dictionary safely."""
        async with status_lock:
            return latest_car_status.copy()

    async def send_car_updates(self):
        """Continuously send car data updates every 5 seconds."""
        # print("send_car_updates started")
        try:
            while True:
                car_data = await self.get_car_data_from_dict()
                # print("Car Data to be sent:", car_data)  # Debugging
                if car_data:
                    await self.send(text_data=json.dumps({'car_data': car_data}))
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print("send_car_updates task canceled")
        except Exception as e:
            print(f"Error in send_car_updates: {e}")


    async def car_update_event(self, event):
        """Handler for car updates sent via MQTT."""
        # print("Received event in WebSocket:", event)  # Debugging

        try:
            async with status_lock:
                if isinstance(event['data'], list):
                    for item in event['data']:
                        if isinstance(item, dict):
                            latest_car_status.update(item)
                elif isinstance(event['data'], dict):
                    latest_car_status.update(event['data'])
                else:
                    print("Received invalid data format:", event['data'])

        except Exception as e:
            print(f"Error updating car status: {e}")

        print("Updated latest_car_status:", latest_car_status)  # Debugging

        # Send data to WebSocket clients
        await self.send(text_data=json.dumps({
            'type': 'car_update_event',
            'data': event['data']
        }))


# latest_car_status = {}
# class CarStatusConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = 'car_status_group'
        
#         # Join the group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         await self.accept()

#         # Start an async loop to push updates periodically
#         asyncio.create_task(self.send_car_updates())

#     async def disconnect(self, close_code):
#         # Leave the group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     def get_car_data_from_dict(self):
#         """Fetch the latest car data from the in-memory dictionary."""
#         return latest_car_status

#     async def send_car_updates(self):
#         print("send_car_updates")
#         """Continuously send car data updates every 3 seconds."""
#         while True:
#             car_data = await sync_to_async(self.get_car_data_from_dict)()
#             print("car_data", car_data)
#             # If there's new car data, send it to WebSocket clients
#             if car_data:
#                 await self.send(text_data=json.dumps({'car_data': car_data}))
#             await asyncio.sleep(5)  # Send updates every 3 seconds

#     async def car_update_event(self, event):
#         """
#         Handler for car updates sent via MQTT. This method is called by the group_send
#         to broadcast messages to WebSocket clients.
#         """
#         # Assuming `event['data']` is a list of dictionaries or other structure
#         print("Received websocket data:", event['data'])
#         try:
#             print("Received websocket data:", event['data'])
#             if isinstance(event['data'], list):
#                 # Handle the case where event['data'] is a list of dictionaries
#                 for item in event['data']:
#                     if isinstance(item, dict):
#                         latest_car_status.update(item)
#             elif isinstance(event['data'], dict):
#                 # Handle the case where event['data'] is a single dictionary
#                 latest_car_status.update(event['data'])
#             else:
#                 # Handle invalid format case
#                 print("Received data format is invalid:", event['data'])
#         except Exception as e:
#             print(f"Error updating car status: {e}")

#         # Now, send the updated car data to WebSocket clients
#         print(event['data'])
#         await self.send(text_data=json.dumps({
#             'type': 'car_update_event',
#             'data': event['data']
#         }))


# class CarStatusConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = 'car_status_group'
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#         # Start an async loop to push updates periodically
#         asyncio.create_task(self.send_car_updates())

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     @sync_to_async
#     def get_car_data(self):
#         """Fetch the latest car data from the database."""
#         cars = Car.objects.all().values(
#             'id', 'latitude', 'longitude', 'door_status', 
#             'engine_status', 'speed', 'fuel_level', 
#             'reservation_status', 'updated_at'
#         )
#         for car in cars:
#             car['updated_at'] = car['updated_at'].isoformat() 
#         return list(cars)

#     async def send_car_updates(self):
#         """Continuously send car data updates every 3 seconds."""
#         while True:
#             car_data = await self.get_car_data()
#             await self.send(text_data=json.dumps({'car_data': car_data}))
#             await asyncio.sleep(0.2)  # Send updates every 3 seconds

# In-memory dictionary to hold the car status