from paho.mqtt import client as mqtt_client

broker = '10.42.0.1'
port = 1883
client_id = f'raspi'
username = 'bewohner'
password = 'keinbewohner'

speed_topic = "leds/speed"
brightness_topic = "leds/brightness"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, last):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
            return None
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

class MQTTListener:

    def __init__(self, controller) -> None:
        self.controller = controller

        self.client = connect_mqtt()
        if self.client == None: 
            self.controller.error()

        self.subscribe()

    def start(self):
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
            if msg.topic == speed_topic:
                try: 
                    speed = float(msg.payload.decode())
                    speed = max(0, min(speed, 1))
                    self.controller.set_speed(speed)
                except:
                    pass
            elif msg.topic == brightness_topic: 
                try: 
                    brighntess = float(msg.payload.decode())
                    brighntess = max(0, min(brighntess, 1))
                    self.controller.set_brightness(brighntess)
                except:
                    pass
        
    def subscribe(self):
        self.client.subscribe(speed_topic)
        self.client.subscribe(brightness_topic)
        self.client.on_message = self.on_message

        