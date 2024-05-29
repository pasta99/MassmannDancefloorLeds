import numpy as np
from enum import Enum
from random import randint

class ColorMode(Enum):
    SET = 1
    RANDOM = 2    

class PatternGeneratorBase:
    
    def __init__(self, num_stripes, leds_per_stripe, default_color, bpm) -> None:
        self.num_stripes = num_stripes
        self.leds_per_stripe = leds_per_stripe
        self.set_color(default_color)
        self.color_mode = ColorMode.SET
        self.bpm = self.set_bpm(bpm)

        self.last_color_change = 0

        self.array = np.zeros(shape=(num_stripes, leds_per_stripe, 4))

    def get_frame(self, t):
        print("NOT IMPLEMENTED")
        return self.array
    
    def set_color(self, color):
        self.color = color

    def set_color_mode(self, color_mode):
        self.color_mode = color_mode

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.color_change_interval = 60 / self.bpm

    def change_color_if_necessary(self, t):
        if self.color_mode == ColorMode.RANDOM:
            if t - self.last_color_change > self.color_change_interval:
                self.last_color_change = t
                self.color = [randint(0, 255) for _ in range(3)]

class PatternGeneratorSolid(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe, default_color, bpm) -> None:
        super().__init__(num_stripes, leds_per_stripe, default_color, bpm)

    def get_frame(self, t):
        self.change_color_if_necessary(t)
        self.array[:, :, 0:3] = self.color
        self.array[:, :, 3] = 1
        return self.array