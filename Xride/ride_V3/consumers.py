# consumers.py
import json
import asyncio
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

# Redis client setup (update the connection URL)
redis_client = redis.StrictRedis.from_url(
    'rediss://red-cjcsrendb61s739bj610:B59haYUZ3iFrOM9g0mzbWubr2ZfReoIc@oregon-redis.render.com:6379',
)

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

    async def send_car_updates(self):
        """Continuously send car data updates every 10.5 seconds."""
        try:
            while True:
                # Fetch all car data from Redis and send each car's data separately
                car_keys = redis_client.keys("car:*")

                if not car_keys:
                    await asyncio.sleep(.5)
                    continue

                for key in car_keys:
                    car_info = redis_client.get(key)
                    if car_info:
                        car_data = {key.decode(): json.loads(car_info)}

                        # Send each car's data as an individual message
                        await self.channel_layer.group_send(
                            "car_status_group",
                            {
                                "type": "car_update_event",
                                "data": car_data,
                            }
                        )

                await asyncio.sleep(1)  # Sleep for 10.5 seconds
        except asyncio.CancelledError:
            print("send_car_updates task canceled")
        except Exception as e:
            print(f"Error in send_car_updates: {e}")

    async def car_update_event(self, event):
        """Handler for car updates sent via MQTT."""
        try:
            # Save data to Redis, ensuring TTL is set for 30 seconds
            if isinstance(event['data'], list):
                for item in event['data']:
                    if isinstance(item, dict):
                        car_id = item.get('car-id') or item.get('car_id')
                        if car_id:
                            redis_client.set(f"car:{car_id}", json.dumps(item), ex=30)  # Set a 30 seconds TTL
            elif isinstance(event['data'], dict):
                car_id = event['data'].get('car-id') or event['data'].get('car_id')
                if car_id:
                    redis_client.set(f"car:{car_id}", json.dumps(event['data']), ex=30)  # Set a 30 seconds TTL

        except Exception as e:
            print(f"Error updating Redis with car status: {e}")

        # Send the updated car data to WebSocket clients as one car at a time
        print("event['data']", event['data'])
        await self.send(text_data=json.dumps({
            'type': 'car_update_event',
            'data': event['data']
        }))

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