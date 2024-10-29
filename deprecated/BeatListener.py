import pyaudio
import aubio
import numpy as np
from time import sleep
 

from paho.mqtt import client as mqtt_client
import time
import random 

broker = '10.151.250.125'
port = 1883
topic = "leds/beat"
client_id = f'beat_listener-mqtt'
username = 'bewohner'
password = 'keinbewohner'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, last):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    # client = mqtt_client.Client(client_id)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
    
def publish(client):
	msg = "." #f"{random.random()}"
	result = client.publish(topic, msg)
	status = result[0]
	if status == 0:
		print(f"Send `{msg}` to topic `{topic}`")
	else:
		print(f"Failed to send message to topic {topic}")
 
bufferSize = 256
windowSizeMultiple = 2 # or 4 for higher accuracy, but more computational cost
 
audioInputDeviceIndex = 8 # use 'arecord -l' to check available audio devices
audioInputChannels = 1
 
 
# create the aubio tempo detection:
hopSize = bufferSize
winSize = hopSize * windowSizeMultiple
tempoDetection = aubio.tempo(method='default', buf_size=512, hop_size=hopSize, samplerate=44100)
 
client = connect_mqtt()
 
# this function gets called by the input stream, as soon as enough samples are collected from the audio input:
def readAudioFrames(in_data, frame_count, time_info, status):
 
    signal = np.frombuffer(in_data, dtype=np.float32)
 
    beat = tempoDetection(signal)
    if beat:
        bpm = tempoDetection.get_bpm()
        print("beat! (running with "+str(bpm)+" bpm)")
        publish(client)
 
    return (in_data, pyaudio.paContinue)
 
 
# create and start the input stream
pa = pyaudio.PyAudio()
audioInputDevice = pa.get_device_info_by_index(audioInputDeviceIndex)
audioInputSampleRate = int(audioInputDevice['defaultSampleRate'])
inputStream = pa.open(format=pyaudio.paFloat32,
                input=True,
                channels=audioInputChannels,
                input_device_index=audioInputDeviceIndex,
                frames_per_buffer=bufferSize,
                rate=audioInputSampleRate,
                stream_callback=readAudioFrames)
 
 
# because the input stream runs asynchronously, we just wait for a few seconds here before stopping the script:
try: 
    while True:
        sleep(20000)
except: 
    inputStream.stop_stream()
    inputStream.close()
    pa.terminate()