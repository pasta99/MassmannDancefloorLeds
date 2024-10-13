import numpy as np
from enum import Enum
from random import randint, random
import colorsys
import math

class ColorMode(Enum):
    SET = 1
    RANDOM = 2    


def id_to_coord(x, y):
    return x * 0.03, y * 0.64

def clip_intensity(x):
        return max(0, min(1, x))

def combine_color_brightness(color, brightness):
    comb = np.zeros(shape=(4))
    comb[:3] = color
    comb[3] = brightness
    return comb

def get_random_color_diff(color_before):
    current_hsv = colorsys.rgb_to_hsv(color_before[0], color_before[1], color_before[2])
    current_h = current_hsv[0]
    new_h = random()
    while abs(current_h - new_h) < 0.05:
        new_h = random()

    new_rgb = colorsys.hsv_to_rgb(new_h, 1, 1)

    new_rgb_list = [255 * c for c in new_rgb]
    return new_rgb_list

def spike_sin(t):
        t_n = t % 2
        if t_n < 1:
            return t_n
        else: 
            return 2 - t_n
        
def spike_sin_d(t):
    t_n = t % 2
    if t_n < 1:
        return 1
    else: 
        return -1
        
def normalized_sin(t):
    return 0.5 * (math.sin(t) + 1)

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

class Beam:
    def __init__(self, pos, length, speed, color):
        self.pos = pos
        self.length = length
        self.speed = speed
        self.color = color

    def advance(self, dt):
        self.pos += self.speed * dt  

class PatternGeneratorBase:
    
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        self.num_stripes = num_stripes
        self.leds_per_stripe = leds_per_stripe
        self.t = 0
        self.color_mode = ColorMode.SET
        self.set_bpm(100)
        self.speed = 1

        self.color = [255, 0, 0]

        self.current_color = self.color

        self.last_color_change = 0

        self.array = np.zeros(shape=(num_stripes, leds_per_stripe, 4))
    
    def reset_array(self):
        self.array = np.zeros(shape=(self.num_stripes, self.leds_per_stripe, 4))

    def fill_stripe(self, idx, color):
        single_stripe = np.tile(color, (self.leds_per_stripe, 1))
        self.array[idx] = single_stripe

    def next_frame(self, dt):
        print("NOT IMPLEMENTED")
        return self.array
    
    def set_color(self, color):
        self.color = color

    def is_random_color(self):
        return self.color_mode == ColorMode.RANDOM

    def set_color_mode(self, color_mode):
        self.color_mode = color_mode
        if color_mode == ColorMode.SET:
            self.current_color = self.color

    def get_color(self):
        if self.is_random_color():
            return self.current_color
        else:
            return self.color

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.color_change_interval = 180 / self.bpm

    def change_color_if_necessary(self):
        if self.color_mode == ColorMode.RANDOM:
            current_hsv = colorsys.rgb_to_hsv(self.current_color[0], self.current_color[1], self.current_color[2])
            current_h = current_hsv[0]
            new_h = random()
            while abs(current_h - new_h) < 0.05:
                new_h = random()

            new_rgb = colorsys.hsv_to_rgb(new_h, 1, 1)

            new_rgb_list = [255 * c for c in new_rgb]

            self.current_color = new_rgb_list

    def beat(self):
        pass

    def set_speed(self, speed):
        self.speed = speed
class PatternGeneratorSolid(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

    def next_frame(self, dt):
        self.t += dt 
        self.array[:, :, 0:3] = self.current_color
        self.array[:, :, 3] = 1
        return self.array
    
    def beat(self):
        self.change_color_if_necessary()

class PatternGeneratorWave(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.shift = 0
        self.direction = 1

    def beat(self):
        self.change_color_if_necessary()

        # self.direction *= -1
        

    def next_frame(self, dt):
        self.t += dt
        self.array[:, :, 0:3] = self.current_color

        self.shift += dt * 5 * self.direction

        brightness = np.arange(0, self.leds_per_stripe)
        sin_lambda = lambda x: (np.sin(x / 1 + self.shift) + 1) / 2
        func = np.vectorize(sin_lambda)

        brightness = func(brightness)

        for i in range(self.num_stripes):
            self.array[i, :, 3] = brightness
        return self.array
    
class PatternGeneratorStrobo(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.set_color((255, 255, 255))
        self.last_toggle = 0
        self.on = True

        self.array[:, :, 0:3] = np.array([255, 255, 255])


    def next_frame(self, dt):
        self.t += dt

        if self.t - self.last_toggle > 0.01: 
            self.last_toggle = self.t
            self.on = not self.on 

        brightness = 1 if self.on else 0

        for i in range(self.num_stripes):
            if random() < 0.5:
                self.array[i, :, 3] = brightness
            else:
                self.array[i, :, 3] = 0

        return self.array

class PatternGeneratorBeams(PatternGeneratorBase): 
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

        self.standard_beam_length = 10

        self.min_speed = 50
        self.max_speed = 120
        self.standard_beam_speed = 80

        self.beams = []

        for i in range(self.num_stripes):
            self.beams.append([])
            self.create_beam(i, randint(0, 80), random() < 0.5)

    def beat(self):
        print("Got beat to generator")

    def get_color_for_beam(self):
        if self.color_mode == ColorMode.SET:
            return self.color
        return get_random_color_diff([0, 0, 0])

    def create_beam(self, beam_nr, pos, reverse):
        beam_pos = pos
        beam_length = self.standard_beam_length
        beam_speed = self.standard_beam_speed

        beam_color = [255, 0, 0]

        if reverse: 
            beam_speed *= -1

        beam = Beam(beam_pos, beam_length, beam_speed, beam_color)

        self.beams[beam_nr].append(beam)

    def set_color(self, color):
        self.color = color

        for beams_per_stripe in self.beams:
            for beam in beams_per_stripe:
                beam.color = color

    def set_speed(self, speed):
        beam_speed = np.interp(speed, [0, 1], [self.min_speed, self.max_speed])
        for beams_per_stripe in self.beams:
            for beam in beams_per_stripe:
                if beam.speed < 0:
                    beam.speed = -beam_speed
                else:
                    beam.speed = beam_speed

    def next_frame(self, dt):
        self.t += dt


        evtl_new_random_color = get_random_color_diff(self.beams[0][0].color)
        if self.beams[0][0].pos > self.leds_per_stripe + self.beams[0][0].length or self.beams[0][0].pos < -self.beams[0][0].length:
            if self.is_random_color():
                self.current_color = evtl_new_random_color

        for i in range(len(self.beams)):
            for j in range(len(self.beams[i])):
                if self.beams[i][j].pos > self.leds_per_stripe + self.beams[i][j].length:
                    self.beams[i][j].pos = self.leds_per_stripe
                    self.beams[i][j].speed *= -1
                if self.beams[i][j].pos < -self.beams[i][j].length:
                    self.beams[i][j].pos = 0
                    self.beams[i][j].speed *= -1

                self.beams[i][j].advance(dt)

        for stripe_nr in range(self.num_stripes):
            stripe = np.zeros(shape=(self.leds_per_stripe, 4))
            for i in range(self.leds_per_stripe):
                for beam in self.beams[stripe_nr]:
                    dist = i - beam.pos
                    if abs(dist) < beam.length: 
                        dist = abs(dist)
                        b = 1 - dist / beam.length
                        b = clip_intensity(b)
                        stripe[i, :3] = np.array(self.current_color)
                        stripe[i, 3] = b

            self.array[stripe_nr] = stripe.copy()

        return self.array

class HorizontalWavePhase(Enum):
    ASC = 0
    DESC = 1
    WAIT = 2

class PatternGeneratorHorizontalWave(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.phase = HorizontalWavePhase.ASC
        self.last_event = 0
        self.activated_stripes = 0
        self.deactivated_stripes = 0
        self.color = [255, 0, 0]
        self.current_color = [255, 0, 0]

        self.min_delay = 0.001
        self.max_delay = 0.05

        self.delay = 0.005

    def set_speed(self, speed):
        self.delay = np.interp(1 - speed, [0, 1], [self.min_delay, self.max_delay])

    def fill_stripe(self, idx, color):
        single_stripe = np.tile(color, (self.leds_per_stripe, 1))
        self.array[idx] = single_stripe

    def next_frame(self, dt):
        self.t += dt
        
        if self.phase == HorizontalWavePhase.ASC:
            if self.t - self.last_event > self.delay:
                self.last_event = self.t
                for i in range(self.activated_stripes):
                    self.fill_stripe(i, combine_color_brightness(self.get_color(), 1))
                self.activated_stripes += 1

                if self.activated_stripes == self.num_stripes + 1:
                    self.activated_stripes = 0
                    self.phase = HorizontalWavePhase.DESC

        elif self.phase == HorizontalWavePhase.DESC:
            if self.t - self.last_event > self.delay:
                self.last_event = self.t
                for i in range(self.deactivated_stripes):
                    self.fill_stripe(i, combine_color_brightness(self.get_color(), 0))
                self.deactivated_stripes += 1

                if self.deactivated_stripes == self.num_stripes + 1:
                    self.phase = HorizontalWavePhase.ASC
                    self.deactivated_stripes = 0
                    if self.is_random_color():
                        self.current_color = get_random_color_diff(self.get_color())

        return self.array

class PatternGeneratorTwoBeams(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

        self.beam1_pos = 0
        self.beam2_pos = 12

        self.min_speed = 7
        self.max_speed = 25
        self.speed = 10

        self.beam1_speed = self.speed
        self.beam2_speed = -self.speed

    def set_speed(self, speed):
        self.speed = np.interp(speed, [0, 1], [self.min_speed, self.max_speed])
        self.beam1_speed = np.sign(self.beam1_speed) * self.speed
        self.beam2_speed = np.sign(self.beam2_speed) * self.speed

    def next_frame(self, dt):
        self.t += dt
        self.beam1_pos += self.beam1_speed * dt
        self.beam2_pos += self.beam2_speed * dt

        if self.beam1_pos > 6:
            self.beam1_pos = 6
            self.beam1_speed *= -1
            if self.is_random_color():
                self.current_color = get_random_color_diff(self.get_color())
        if self.beam1_pos < -1:
            self.beam1_pos = -1
            self.beam1_speed *= -1

        if self.beam2_pos < 6:
            self.beam2_pos = 6
            self.beam2_speed *= -1
        if self.beam2_pos > 13:
            self.beam2_pos = 13
            self.beam2_speed *= -1

        for i in range(self.num_stripes):
            dist1 = abs(self.beam1_pos - i)
            dist2 = abs(self.beam2_pos - i)
            b1 = np.interp(dist1, [0, 0.5, 1], [1, 1, 0])
            b2 = np.interp(dist2, [0, 0.5, 1], [1, 1, 0])

            b = max(b1, b2)

            self.fill_stripe(i, np.array(combine_color_brightness(self.get_color(), b)))
            
        return self.array

class PatternGeneratorLighthouse(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.radius = 0
        self.min_speed = 5
        self.max_speed = 12

        self.speed = 5

        self.max_radius = 1

    def set_speed(self, speed):
        self.speed = np.interp(speed, [0, 1], [self.min_speed, self.max_speed])

    def next_frame(self, dt):
        self.t += dt

        self.radius += self.speed * dt
        if self.radius > self.max_radius:
            self.radius = self.max_radius
            self.speed *= -1
        if self.radius < 0:
            self.radius = 0
            self.speed *= -1

        for x in range(self.leds_per_stripe):
            for y in range(self.num_stripes):

                x_norm = x * 0.03
                y_norm = y * 0.16

                dist1, angle = cart2pol(x_norm, y_norm)
                
                b1 = 1 if dist1 < self.radius else 0

                x_norm = (self.leds_per_stripe - x) * 0.03
                y_norm = y * 0.16

                dist2, angle = cart2pol(x_norm, y_norm)
                b2 = 1 if dist2 < self.radius else 0

                b = max(b1, b2)                

                self.array[y, x] = combine_color_brightness(self.get_color(), b)

        if self.radius < 0.01: 
            if self.is_random_color():
                self.current_color = get_random_color_diff(self.get_color())
        
        return self.array
    

class PatternGeneratorSpots(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.stripes_on = []
        self.next_toggle = []

        for i in range(self.num_stripes):
            self.stripes_on.append(False)
            self.next_toggle.append(random() * 5)

        self.min_delay = 0.1
        self.max_delay = 0.5

        self.delay = 0.5

    def fill_spot(self, idx, start, end, color):
        self.array[idx, start:end] = np.tile(color, (end - start, 1))
        
    def toggle(self, idx):
        start = randint(0, self.leds_per_stripe)
        end = min(start + 10, self.leds_per_stripe)
        if self.stripes_on[idx]:
            if self.is_random_color():
                new_color =  get_random_color_diff([0, 0, 0])
            else:
                new_color =  self.color
            self.fill_spot(idx, start, end, combine_color_brightness(new_color, 1))
            self.next_toggle[idx] = self.t + self.delay
        else:
            self.fill_stripe(idx, [0, 0, 0, 0])
            self.next_toggle[idx] = self.t + 0.01

        self.stripes_on[idx] = not self.stripes_on[idx]

    def set_speed(self, speed):
        self.delay = np.interp(1 - speed, [0, 1], [self.min_delay, self.max_delay])

    def next_frame(self, dt):
        self.t += dt

        for i in range(len(self.next_toggle)):
            if self.next_toggle[i] < self.t:
                self.toggle(i)
        
        return self.array