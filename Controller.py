import numpy as np
import time

from PatternGenerator import PatternGeneratorSolid
from LEDDisplay import LEDDisplay

MIN_BPM = 50
MAX_BPM = 250

FRAME_RATE = 1/20

NUM_STRIPES = 10
LEDS_PER_STRIPE = 60 * 4

DEFAULT_COLOR = [255, 0, 0]

class Controller: 

    def __init__(self) -> None:
        self.brightness = 0.5
        self.bpm = 0
        self.set_speed(0.5)
        self.on = True
        self.color = DEFAULT_COLOR

        self.t = 0

        self.strobo = False

        self.generator = PatternGeneratorSolid(NUM_STRIPES, LEDS_PER_STRIPE, self.color, self.bpm)

        self.display = LEDDisplay(None)

    def set_speed(self, relative_speed):
        self.bpm = np.interp(relative_speed, [0, 1], [MIN_BPM, MAX_BPM])
        print(f"New bpm: {self.bpm}")

    def set_brightness(self, brightness):
        self.brightness = brightness
        print(f"New brightness: {self.brightness}")

    def set_r(self, r):
        self.color[0] = r * 255
        self.generator.set_color(self.color)
    def set_g(self, g):
        self.color[1] = g * 255
        self.generator.set_color(self.color)
    def set_b(self, b):
        self.color[2] = b * 255
        self.generator.set_color(self.color)

    def set_color_mode(self, mode):
        self.generator.set_color_mode(mode)
        self.generator.set_color(self.color)

    def set_on(self, on):
        self.on = on

    def set_strobo(self, on):
        pass

    def set_mode(self, mode_id):
        pass

    def error(self):
        print("ERROR")

    def main_loop(self):
        while True:
            if self.on:
                frame = self.generator.get_frame(self.t)
                self.display.show(frame)
            time.sleep(FRAME_RATE)
            self.t += FRAME_RATE
 
if __name__ == "__main__":
    c = Controller()
    c.set_speed(1)

    print(c.bpm)

