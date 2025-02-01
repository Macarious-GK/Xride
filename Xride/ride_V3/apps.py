# from django.apps import AppConfig

# class RideV3Config(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'ride_V3'

#     def ready(self):
#         # Import mqtt_subscriber_cloud only when the app is ready
#         from . import mqtt_subscriber_cloud  # Import inside the ready method
#         mqtt_subscriber_cloud.client.loop_forever()# Call the function as needed


from django.apps import AppConfig
import threading

class RideV3Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ride_V3'

    def ready(self):
        # Import mqtt_subscriber_cloud only when the app is ready
        from . import mqtt_subscriber_cloud

        # Start the MQTT subscriber in a background thread
        mqtt_thread = threading.Thread(target=mqtt_subscriber_cloud.start_mqtt_client)
        mqtt_thread.daemon = True  # Ensures the thread will exit when the main program exits
        mqtt_thread.start()
