import numpy as np
import time

MIN_BPM = 50
MAX_BPM = 250

FRAME_RATE = 1/20

class Controller: 

    def __init__(self) -> None:
        self.brightness = 0.5
        self.bpm = 0
        self.set_speed(0.5)
        self.on = True

    def set_speed(self, relative_speed):
        self.bpm = np.interp(relative_speed, [0, 1], [MIN_BPM, MAX_BPM])
        print(f"New bpm: {self.bpm}")

    def set_brightness(self, brightness):
        self.brightness = brightness
        print(f"New brightness: {self.brightness}")

    def error(self):
        print("ERROR")

    def main_loop(self):
        while True:
            if self.on:
                print(".")
            time.sleep(FRAME_RATE)
 
if __name__ == "__main__":
    c = Controller()
    c.set_speed(1)

    print(c.bpm)

