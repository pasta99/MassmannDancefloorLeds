from paho.mqtt import client as mqtt_client

from PatternGenerator import ColorMode

broker = '10.42.0.1'
port = 1883
client_id = f'raspi'
username = 'bewohner'
password = 'keinbewohner'

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

        self.topics_action = {
            "leds/speed": self.handle_speed,
            "leds/brightness": self.handle_brightness,
            "leds/color/r": self.handle_r, 
            "leds/color/g": self.handle_g, 
            "leds/color/b": self.handle_b, 
            "leds/color/mode": self.handle_color_mode,
            "leds/toggle": self.handle_toggle, 
            "leds/strobo": self.handle_strobo,
            "leds/mode": self.handle_mode
        }
    
        self.subscribe()

    def start(self):
        self.client.loop_forever()

    def handle_speed(self, msg):
        try: 
            speed = float(msg.payload.decode())
            speed = max(0, min(speed, 1))
            self.controller.set_speed(speed)
        except:
            print("Could not decode a number. Abort!")
    def handle_brightness(self, msg):
        try: 
            brightness = float(msg.payload.decode())
            brightness = max(0, min(brightness, 1))
            self.controller.set_brightness(brightness)
        except:
            print("Could not decode a number. Abort!")

    def handle_r(self, msg):
        try: 
            r = float(msg.payload.decode())
            r = max(0, min(r, 1))
            self.controller.set_r(r)
        except:
            print("Could not decode a number. Abort!")
    def handle_g(self, msg):
        try: 
            g = float(msg.payload.decode())
            g = max(0, min(g, 1))
            self.controller.set_g(g)
        except:
            print("Could not decode a number. Abort!")
    def handle_b(self, msg):
        try: 
            b = float(msg.payload.decode())
            b = max(0, min(b, 1))
            self.controller.set_b(b)
        except:
            print("Could not decode a number. Abort!")

    def handle_color_mode(self, msg):
        txt = msg.payload.decode()
        if txt == "set":
            self.controller.set_color_mode(ColorMode.SET)
        elif txt == "random":
            self.controller.set_color_mode(ColorMode.RANDOM)

    def handle_toggle(self, msg):
        txt = msg.payload.decode()
        if txt == "on":
            self.controller.on(True)
        elif txt == "off":
            self.controller.on(False)

    def handle_strobo(self, msg):
        txt = msg.payload.decode()
        if txt == "on":
            self.controller.strobo(True)
        elif txt == "off":
            self.controller.strobo(False)

    def handle_mode(self, msg):
        txt = msg.payload.decode()
        try:
            id = int(float(txt))
            self.controller.set_mode(id)
        except:
            print("Could not decode a number. Abort!")

    def on_message(self, client, userdata, msg):
        for topic, action in self.topics_action.items():
            if msg.topic == topic:
                action(msg)
        
    def subscribe(self):
        for t in self.topics_action.keys():
            self.client.subscribe(t)
        self.client.on_message = self.on_message