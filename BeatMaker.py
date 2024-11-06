from paho.mqtt import client as mqtt_client
import time

port = 1883
client_id = f'beatmaker22'
username = 'bewohner'
password = 'keinbewohner'
broker = '10.151.250.126'

def connect_mqtt(on_connect):
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

class BeatMaker:
    def __init__(self) -> None:
        self.running = True
        self.beat_channel = "leds/beat"
        self.activate_beat_maker_channel = "leds/beat/auto/activate"
        self.deactivate_beat_maker_channel = "leds/beat/auto/deactivate"
        self.bpm = 60
        self.waiting_time = 60 / self.bpm

        self.client = connect_mqtt(self.on_connect)
        self.main_loop()
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc, last):
        if rc == 0:
            print("Connected to MQTT Broker!")
            self.subscribe()
        else:
            print("Failed to connect, return code %d\n", rc)
            return None

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.waiting_time = 60 / bpm

    def on_message(self, client, userdata, msg):
        if msg.topic == self.activate_beat_maker_channel:
            try: 
                bpm = int(msg.payload.decode())
            except:
                bpm = 100
            self.set_bpm(bpm)
            self.running = True
        if msg.topic == self.deactivate_beat_maker_channel: 
            self.running = False
        
    def subscribe(self):    
        print("Subscribing") 
        self.client.subscribe(self.activate_beat_maker_channel)
        self.client.subscribe(self.deactivate_beat_maker_channel)
        self.client.on_message = self.on_message

    def send_beat(self):
        self.client.publish(self.beat_channel, str(self.bpm))

    def main_loop(self):
        while True: 
            while (self.running):
                self.send_beat()
                # print(f"Sent beat BPM: {self.bpm} Waittime: {self.waiting_time}")
                time.sleep(self.waiting_time)
                self.client.loop()
            self.client.loop()
            time.sleep(1/20)

import threading
if __name__ == "__main__":
    b = BeatMaker()
