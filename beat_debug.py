# from paho.mqtt import client as mqtt_client
# import time

port = 1883
client_id = f'beatmaker_debug'
username = 'bewohner'
password = 'keinbewohner'
broker = '10.42.0.1'

# def connect_mqtt():
#     def on_connect(client, userdata, flags, rc, last):
#         if rc == 0:
#             print("Connected to MQTT Broker!")
#         else:
#             print("Failed to connect, return code %d\n", rc)
#             return None
#     client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

#     client.username_pw_set(username, password)
#     client.on_connect = on_connect
#     client.connect(broker, port)
#     return client

# if __name__ == "__main__":
#     client = connect_mqtt()
#     client.loop_start()
#     result = client.publish("leds/beat/auto/deactivate/", "AAA")
#     result = client.publish("leds/beat/auto/activate/", "AAA")
#     result = client.publish("leds/beat/", "AAA")
#     print("BABABA")
#     status = result[0]
#     if status == 0:
#         print(f"Success")
#     else:
#         print(status)
#         print(f"Failed to send message to topic")
#     client.loop()
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected! Result code: " + str(rc))

client = mqtt.Client(client_id=client_id)
client.on_connect = on_connect
client.username_pw_set(username=username, password=password)
client.loop_start()
client.connect(broker, port)

# time.sleep
client.publish("leds/beat/auto/deactivate/", "test", qos=2)