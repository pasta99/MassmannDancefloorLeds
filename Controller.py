import numpy as np
import time
import board
import threading

from PatternGenerator import PatternGeneratorTimingTest, PatternGeneratorSolid, PatternGeneratorWave, PatternGeneratorStrobo, ColorMode, PatternGeneratorBeams, PatternGeneratorHorizontalWave, PatternGeneratorTwoBeams, PatternGeneratorLighthouse, PatternGeneratorSpots
from LEDDisplay import LEDDisplay, LEDDisplayReal
from ManualBeatMaker import ManualBeatMaker

MIN_BPM = 50
MAX_BPM = 250
DEFAULT_BPM = 100

FRAME_RATE = 0.059
NUM_STRIPES = 12 #10
LEDS_PER_STRIPE = 80

DEFAULT_COLOR = [255, 0, 0]

DATA_PIN = board.D18

possible_generators = [PatternGeneratorTimingTest, PatternGeneratorBeams, PatternGeneratorHorizontalWave, PatternGeneratorTwoBeams, PatternGeneratorLighthouse, PatternGeneratorSpots]

class Controller: 

    def __init__(self) -> None:
        self.color = DEFAULT_COLOR
        self.generator = possible_generators[1](NUM_STRIPES, LEDS_PER_STRIPE)
        self.brightness = 0.5
        self.on = True
        self.t = 0
        self.bpm = 0
        self.relative_speed = 0
        self.strobo = False
        self.color_mode = ColorMode.SET
        self.strobo_generator = PatternGeneratorStrobo(NUM_STRIPES, LEDS_PER_STRIPE)

        self.display = LEDDisplayReal(DATA_PIN, NUM_STRIPES, LEDS_PER_STRIPE, self.brightness)
        
        # self.beat_maker = ManualBeatMaker(self.beat, self.bpm)
        # threading.Thread(target=self.beat_maker.main_loop).start()
        self.set_speed(0.5)
        

    def set_generator(self, id):
        if id >= len(possible_generators): 
            print("ID out of range")
            id = 0
        self.generator = possible_generators[id](NUM_STRIPES, LEDS_PER_STRIPE)
        self.generator.set_color(self.color)
        self.generator.set_color_mode(self.color_mode)
        self.generator.set_bpm(self.bpm)
        self.generator.set_speed(self.relative_speed)

    def set_speed(self, relative_speed):
        self.relative_speed = relative_speed
        self.bpm = np.interp(relative_speed, [0, 1], [MIN_BPM, MAX_BPM])
        # self.beat_maker.set_bpm(self.bpm)
        self.generator.set_bpm(self.bpm)
        self.generator.set_speed(relative_speed)
        print(f"New bpm: {self.bpm}")

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.display.set_brighness(brightness)
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
        self.color_mode = mode
        self.generator.set_color_mode(mode)
        self.generator.set_color(self.color)

    def set_on(self, on):
        self.on = on
        if self.on == False:
            self.display.clear_all()

    def set_strobo(self, on):
        self.strobo = on

    def set_mode(self, mode_id):
        self.set_generator(mode_id)

    def error(self):
        print("ERROR")

    def beat(self, bpm):
        self.generator.beat(bpm)

    def main_loop(self):
        while True:
            if self.on:
                frame = self.generator.next_frame(FRAME_RATE)
                if self.strobo:
                    frame = self.strobo_generator.next_frame(FRAME_RATE)
                start_time = time.time()
                self.display.show(frame, strobo=self.strobo)
                end_time = time.time()

                # print(end_time - start_time)
            # time.sleep(FRAME_RATE / 1000)
            self.t += FRAME_RATE
 
if __name__ == "__main__":
    c = Controller()
    c.set_speed(1)

    print(c.bpm)

