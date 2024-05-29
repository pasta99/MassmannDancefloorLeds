import numpy as np
from enum import Enum

class ColorMode(Enum):
    SET = 1
    RANDOM = 2    

class PatternGenerator:
    
    def __init__(self, num_stripes, leds_per_stripe, default_color, bpm) -> None:
        self.num_stripes = num_stripes
        self.leds_per_stripe = leds_per_stripe
        self.set_color(default_color)
        self.color_mode = ColorMode.SET
        self.bpm = bpm

        self.array = np.zeros(shape=(num_stripes, leds_per_stripe, 4))

    def get_frame(self, t):
        return self.array
    
    def set_color(self, color):
        self.color = color

    def set_color_mode(self, color_mode):
        self.color_mode = color_mode

    def set_bpm(self, bpm):
        self.bpm = bpm
    

if __name__ == "__main__":
    p = PatternGenerator(3, 3, (1, 0, 0), 2)

    print(p.get_frame(0)[0, 0])