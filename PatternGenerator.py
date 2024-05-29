import numpy as np
from enum import Enum
from random import randint

class ColorMode(Enum):
    SET = 1
    RANDOM = 2    

class PatternGeneratorBase:
    
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        self.num_stripes = num_stripes
        self.leds_per_stripe = leds_per_stripe
        self.t = 0
        self.set_color([255, 0, 0])
        self.color_mode = ColorMode.SET
        self.set_bpm(100)

        self.last_color_change = 0

        self.array = np.zeros(shape=(num_stripes, leds_per_stripe, 4))

    def next_frame(self, dt):
        print("NOT IMPLEMENTED")
        return self.array
    
    def set_color(self, color):
        self.color = color

    def set_color_mode(self, color_mode):
        self.color_mode = color_mode

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.color_change_interval = 60 / self.bpm

    def change_color_if_necessary(self):
        if self.color_mode == ColorMode.RANDOM:
            if self.t - self.last_color_change > self.color_change_interval:
                self.last_color_change = self.t
                self.color = [randint(0, 255) for _ in range(3)]
        else: 
            self.color 
class PatternGeneratorSolid(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

    def next_frame(self, dt):
        self.t += dt
        self.change_color_if_necessary()
        self.array[:, :, 0:3] = self.color
        self.array[:, :, 3] = 1
        return self.array

class PatternGeneratorWave(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

    def next_frame(self, dt):
        self.t += dt
        self.change_color_if_necessary()
        self.array[:, :, 0:3] = self.color

        brightness = np.arange(0, self.leds_per_stripe)
        sin_lambda = lambda x: (np.sin(x / 4 + self.t * self.bpm / 10) + 1) / 2
        func = np.vectorize(sin_lambda)

        brightness = func(brightness)

        for i in range(self.num_stripes):
            self.array[i, :, 3] = brightness
        return self.array
    
class PatternGeneratorStrobo(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.set_color(255, 255, 255)
        self.last_toggle = 0
        self.on = True

        self.array[:, :, 0:3] = self.color


    def next_frame(self, dt):
        self.t += dt

        if self.t - self.last_toggle > 0.1: 
            self.last_toggle = self.t
            self.on = not self.on 

        brightness = 1 if self.on else 0

        self.array[:, :, 3] = brightness

        return self.array

        