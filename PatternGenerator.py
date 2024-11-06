import numpy as np
from enum import Enum
from random import randint, random, choice
import colorsys
import math

class ColorMode(Enum):
    SET = 1
    RANDOM = 2    

def bpm_to_next_beat_time(bpm):
    return 60 / bpm

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

def rotate_point(x, y, angle):
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    return x * cos_angle - y * sin_angle, y * cos_angle + x * sin_angle

class PatternGeneratorBase:
    
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        self.num_stripes = num_stripes
        self.leds_per_stripe = leds_per_stripe
        self.color_mode = ColorMode.SET

        self.color = [255, 0, 0]
        self.current_random_color = [255, 0, 0]

        self.current_color = self.color

        self.array = np.zeros(shape=(num_stripes, leds_per_stripe, 4))

        self.beat_trigger_interval = 1
        self.beat_cycle = 0
        self.framerate = 0.061
    
    def reset_array(self):
        self.array = np.zeros(shape=(self.num_stripes, self.leds_per_stripe, 4))

    def fill_stripe(self, idx, color):
        single_stripe = np.tile(color, (self.leds_per_stripe, 1))
        self.array[idx] = single_stripe

    def next_frame(self):
        print("NOT IMPLEMENTED")
        return self.array
    
    def set_color(self, color):
        self.color = color

    def is_random_color(self):
        return self.color_mode == ColorMode.RANDOM

    def set_color_mode(self, color_mode):
        self.color_mode = color_mode

    def get_color(self):
        if self.is_random_color():
            return self.current_random_color
        else:
            return self.color

    def get_random_position_on_grid(self):
        x = random() * self.leds_per_stripe * 0.05
        y = random() * self.num_stripes * 0.5

        return x, y
    # def set_bpm(self, bpm):
    #     self.bpm = bpm
    #     self.color_change_interval = 180 / self.bpm

    def change_color_if_necessary(self):
        if self.color_mode == ColorMode.RANDOM:
            current_hsv = colorsys.rgb_to_hsv(self.current_color[0], self.current_color[1], self.current_color[2])
            current_h = current_hsv[0]
            new_h = random()
            while abs(current_h - new_h) < 0.05:
                new_h = random()

            new_rgb = colorsys.hsv_to_rgb(new_h, 1, 1)

            new_rgb_list = [255 * c for c in new_rgb]

            self.current_random_color = new_rgb_list

    def beat(self, bpm):
        next_beat_time = bpm_to_next_beat_time(bpm)

        self.beat_cycle += 1 
        self.beat_cycle %= self.beat_trigger_interval

        if self.beat_cycle == 0:
            self.beat_trigger(next_beat_time)

    def beat_trigger(self, time_until_next):
        pass

    def fill_stripe(self, idx, color):
        single_stripe = np.tile(color, (self.leds_per_stripe, 1))
        self.array[idx] = single_stripe

    def fill_spot(self, idx, start, end, color):
        self.array[idx, start:end] = np.tile(color, (end - start, 1))

class PatternGeneratorSolid(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

    def next_frame(self, dt):
        self.array[:, :, 0:3] = self.get_color()
        self.array[:, :, 3] = 1
        return self.array
    
    def beat_trigger(self, time_until_next):
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
        self.t = 0
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

        self.t %= 99999999

        return self.array

class PatternGeneratorSpeakers(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.radius = 0
        self.max_radius = 1

        self.direction = 1

        self.circle_step_size = 0

    def next_frame(self, dt):
        self.radius += self.direction * self.circle_step_size
        if self.radius > self.max_radius:
            self.radius = self.max_radius
            self.direction *= -1

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
          
        return self.array
    
    def beat_trigger(self, time_until_next):
        self.change_color_if_necessary()
        self.radius = -0.15
        self.direction = 1

        self.n_steps = time_until_next / self.framerate
        self.circle_step_size = 2.3 / self.n_steps  
    

class PatternGeneratorSpots(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

        for idx in range(self.num_stripes):
            self.toggle(idx)
        
    def toggle(self, idx):
        start = randint(0, self.leds_per_stripe)
        end = min(start + 10, self.leds_per_stripe)
        self.fill_stripe(idx, [0, 0, 0, 0])
        if self.is_random_color():
            new_color =  get_random_color_diff([0, 0, 0])
        else:
            new_color =  self.color
        self.fill_spot(idx, start, end, combine_color_brightness(new_color, 1))

    def beat_trigger(self, time_until_next):
        change_spots = [random() < 1 for _ in range(self.num_stripes)]
        for idx, change_spots in enumerate(change_spots):
            if change_spots:
                self.toggle(idx)

    def next_frame(self, dt):        
        return self.array


class PatternGeneratorTimingTest(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        
        self.beat_activation = 2
        self.max_size = leds_per_stripe - 1

        self.cycle_time = 2

        self.spot_pos = 0

        self.n_steps = self.cycle_time / self.framerate
        
        self.spot_step_size = self.max_size / self.n_steps

        self.dir = 1

        self.cc = [255, 0, 0]

    def next_frame(self, dt):

        if self.spot_pos >= self.max_size or self.spot_pos <= 0:
            self.dir *= -1

        self.spot_pos += self.dir * self.spot_step_size
        self.spot_pos = max(0, min(self.spot_pos, self.max_size))

        self.reset_array()

        self.array[3][int(self.spot_pos)] = combine_color_brightness(self.cc, 1)
        return self.array
    
    def beat_trigger(self, next_beat_time):
        self.cc = get_random_color_diff(self.cc)
        self.spot_pos = 1

        self.n_steps = next_beat_time / self.framerate
        self.spot_step_size = self.max_size / self.n_steps            

class PatternGeneratorTwoBeams(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

        self.beam1_pos = 0
        self.beam2_pos = 12

        self.beam_step_size = 0
        self.beam1_step_size = self.beam_step_size
        self.beam2_step_size = -self.beam_step_size

        self.beat_trigger_interval = 2

    def set_beam_step_size(self, sz):
        self.beam_step_size = sz
        self.beam1_step_size = self.beam_step_size
        self.beam2_step_size = -self.beam_step_size

    def beat_trigger(self, next_beat_time):
        self.beam1_pos = 0
        self.beam2_pos = 12

        self.n_steps = next_beat_time / self.framerate
        beam_step_size = 6 / self.n_steps

        self.set_beam_step_size(beam_step_size)

    def next_frame(self, dt):
        self.beam1_pos += self.beam1_step_size
        self.beam2_pos += self.beam2_step_size

        if self.beam1_pos > 6:
            self.beam1_pos = 6
            self.beam1_step_size *= -1
            if self.is_random_color():
                self.current_random_color = get_random_color_diff(self.get_color())
        if self.beam1_pos < -1:
            self.beam1_pos = -1
            self.beam2_step_size *= -1

        if self.beam2_pos < 6:
            self.beam2_pos = 6
            self.beam2_step_size *= -1
        if self.beam2_pos > 13:
            self.beam2_pos = 13
            self.beam2_step_size *= -1

        for i in range(self.num_stripes):
            dist1 = abs(self.beam1_pos - i)
            dist2 = abs(self.beam2_pos - i)
            b1 = np.interp(dist1, [0, 0.5, 1], [1, 1, 0])
            b2 = np.interp(dist2, [0, 0.5, 1], [1, 1, 0])

            b = max(b1, b2)

            self.fill_stripe(i, np.array(combine_color_brightness(self.get_color(), b)))
            
        return self.array
        
class PatternGeneratorBeams(PatternGeneratorBase): 
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

        self.standard_beam_length = 10

        self.beams_pos = []
        self.beams_dir = []
        self.beam_step_size = 0

        for i in range(self.num_stripes):
            self.beams_pos.append(randint(0, 80))
            self.beams_dir.append(1 if random() < 0.5 else -1)

        self.beat_trigger_interval = 1
            
    def beat_trigger(self, next_beat_time):
        n_steps = next_beat_time / self.framerate
        self.beam_step_size = (80 / n_steps) / 2
        
        self.change_color_if_necessary()

    def next_frame(self, dt):
        # Move beams 
        new_pos = []
        new_dir = []
        for pos, dir in zip(self.beams_pos, self.beams_dir):
            if pos > self.leds_per_stripe + self.standard_beam_length:
                pos = self.leds_per_stripe
                dir *= -1
            if pos < -self.standard_beam_length:
                pos = 0
                dir *= -1

            new_pos.append(pos + self.beam_step_size * dir)
            new_dir.append(dir)
        self.beams_pos = new_pos
        self.beams_dir = new_dir
        # print(self.beams_pos)

        # Paint beams
        for stripe_nr, pos in enumerate(self.beams_pos):
            stripe = np.zeros(shape=(self.leds_per_stripe, 4))
            for i in range(self.leds_per_stripe):
                dist = i - pos
                if abs(dist) < self.standard_beam_length: 
                    dist = abs(dist)
                    b = 1 - dist / self.standard_beam_length
                    b = clip_intensity(b)
                    stripe[i, :3] = np.array(self.get_color())
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
        self.color = [255, 0, 0]
        self.current_color = [255, 0, 0]

        self.beam_radius = self.num_stripes / 2
        self.start_position = -self.beam_radius
        self.end_position = self.num_stripes + self.beam_radius
        self.beam_pos = self.start_position

        self.beam_step_size = 0

        self.beat_trigger_interval = 4

    def beat_trigger(self, time_until_next):
        self.beam_pos = self.start_position

        self.change_color_if_necessary()

        n_steps = self.beat_trigger_interval * time_until_next / self.framerate
        self.beam_step_size = (self.end_position - self.start_position) / n_steps

    def next_frame(self, dt):
        # Move beam
        self.beam_pos += self.beam_step_size

        # Draw beam
        for stripe_id in range(self.num_stripes):
            dist = stripe_id - self.beam_pos
            b = 1 if abs(dist) < self.beam_radius else 0
            self.fill_stripe(stripe_id, combine_color_brightness(self.get_color(), b))

                # self.array[stripe_id] = stripe.copy()
            
        return self.array

class Beam():
    def __init__(self, position, rotation, direction, step_size, color, width) -> None:
        self.position = position
        self.direction = direction
        self.step_size = step_size

        self.width = width
        self.rotation = rotation

        self.color = color
        self.intensity = 1
    
    def advance(self):
        self.position[0] += self.direction[0] * self.step_size
        self.position[1] += self.direction[1] * self.step_size

    def paint(self, array):
        new_array = np.zeros(shape=array.shape)

        y_indices, x_indices = np.indices(dimensions=(array.shape[0], array.shape[1]))

        # Move indices to real world space (in meters)
        y_indices = y_indices * 0.5
        x_indices = x_indices * 0.05

        # Move rotation anchor to position of beam
        x_shifted = x_indices - self.position[0]
        y_shifted = y_indices - self.position[1]

        # Rotate points
        x_rotated = x_shifted * np.cos(self.rotation) - y_shifted * np.sin(self.rotation)
        # y_rotated = x_shifted * np.sin(self.rotation) + y_shifted * np.cos(self.rotation)

        # Choose all the leds close to beam 
        b_arr = np.maximum(0, 1 - (np.abs(x_rotated) / self.width))

        new_array[..., 3] = b_arr * self.intensity

        mask = new_array[..., 3] > 0
        new_array[mask, :3] = self.color

        return combine_arrays(array, new_array)

def combine_arrays(array1, array2):
    return np.maximum(array1, array2)

class PatternGeneratorRotate(PatternGeneratorBase):

    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.beam = Beam([2, 1], 0, [0, 0], 0, [0, 0, 0], 0.5)

        self.rotation_step_size = 0
        
        self.t = 0

    def beat_trigger(self, time_until_next):
        # print(self.beam.rotation)
        n_steps = time_until_next / self.framerate
        self.rotation_step_size = (math.pi) / n_steps

        # self.change_color_if_necessary()
        self.change_color_if_necessary()
        self.beam.color = self.get_color()
        
        self.t %= 9999999999
    
    def next_frame(self, dt):
        self.t += dt
        self.beam.rotation += self.rotation_step_size
        self.beam.intensity = normalized_sin(10 * self.t)

        self.reset_array()

        self.array = self.beam.paint(self.array)

        return self.array

def get_step_size(time_until_completion, distance_until_completion, framerate):
    n_steps = time_until_completion / framerate
    step_size = distance_until_completion / n_steps
    return step_size


class PatternGeneratorZoom(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.beams = []
        self.beam_width = 0.5

        # self.create_beam(True, 0.3, [255, 0, 0])

        self.rev = False

        self.distance_in_beat = 2

    def create_beam(self, reversed, step_size, color):
        rotation_directions = [([4, 0], np.radians(45), [-1, 1]), ([0, 0], -np.radians(45), [1, 1])]

        if reversed:
            pos, rotation, direction = rotation_directions[0]
        else:
            pos, rotation, direction = rotation_directions[1]

        beam = Beam(pos, rotation, direction, step_size, color, self.beam_width)

        self.beams.append(beam)

    def beat_trigger(self, time_until_next):
        color = get_random_color_diff([0, 0, 0]) if self.is_random_color() else self.color

        step_size = get_step_size(time_until_next, self.distance_in_beat, self.framerate)
        self.create_beam(self.rev, step_size, color)

        self.rev = not self.rev

    def next_frame(self, dt):
        self.reset_array()
        
        for beam in self.beams:
            beam.advance()
            self.array = beam.paint(self.array)

        self.beams = [beam for beam in self.beams if not(beam.position[0] > 5 or beam.position[0] < -1)]

        return self.array
    
class PatternGeneratorZoomAlt(PatternGeneratorZoom):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

        self.beam_width = 0.25
        self.distance_in_beat = 1
        
class PatternGeneratorZoomAlt2(PatternGeneratorZoom):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)

        self.distance_in_beat = 4
    
class Ring:
    def __init__(self, position, outer_r, inner_r, color):
        self.position = position
        self.outer_r = outer_r
        self.inner_r = inner_r

        self.color = color

    def paint(self, array):
        new_array = np.zeros(shape=array.shape)

        y_indices, x_indices = np.indices(dimensions=(array.shape[0], array.shape[1]))

        # Move indices to real world space (in meters)
        y_indices = y_indices * 0.5
        x_indices = x_indices * 0.05

        # Move rotation anchor to position of beam
        x_shifted = x_indices - self.position[0]
        y_shifted = y_indices - self.position[1]

        r = np.sqrt(np.square(x_shifted) + np.square(y_shifted)) 

        # Choose all the leds close to beam 
        # b_arr = np.maximum(0, 1 - (np.abs(r) / max(0.1, self.outer_r)))
        edges = self.outer_r - self.inner_r * 0.2
        b_arr = np.maximum(0, np.interp(r, [self.inner_r, self.inner_r + edges, self.outer_r - edges, self.outer_r], [0, 1, 1, 0]))

        new_array[..., 3] = b_arr

        mask = new_array[..., 3] > 0
        new_array[mask, :3] = self.color

        return combine_arrays(array, new_array)

class PatterGeneratorDrop(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.rings = []
        self.dir = 1

        self.beat_trigger_interval = 1

        self.step_size = 0

    def beat_trigger(self, time_until_next):

        pos = list(self.get_random_position_on_grid())
        color = get_random_color_diff([0, 0, 0]) if self.is_random_color() else self.get_color()

        self.step_size = get_step_size(time_until_next, 2, self.framerate)
        self.rings.append(Ring(pos, 0.1, -0.6, color))

    def next_frame(self, dt):
        self.reset_array()

        for ring in self.rings:

            ring.outer_r += 0.2 * self.dir
            ring.inner_r += 0.2 * self.dir

            self.array = ring.paint(self.array)

        self.rings = [ring for ring in self.rings if ring.outer_r < 5]
        return self.array


class PatterGeneratorSwitch(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.pos = 0
        self.step_size = 0

        self.beat_counter = 0

        self.left_color = self.color
        self.right_color = self.color

    def beat_trigger(self, time_until_next):
        self.step_size = get_step_size(time_until_next, 80, self.framerate)
        if self.beat_counter % 2 == 0:
            self.pos = 0

            if self.is_random_color():
                self.left_color = get_random_color_diff(self.right_color)
            else:
                self.left_color = self.color
        else:
            self.pos = 80
            self.step_size *= -1
            if self.is_random_color():
                self.right_color = get_random_color_diff(self.left_color)
            else:
                self.right_color = self.color
        self.beat_counter += 1

    def next_frame(self, dt):
        self.reset_array()

        for y in range(self.num_stripes):
            if y % 2 == 0:
                # if x_pos < self.pos:
                self.fill_spot(y, 0, min(max(int(self.pos), 0), 80), combine_color_brightness(self.left_color, 1))
            else:
                # if x_pos > self.pos:
                self.fill_spot(y, min(max(int(self.pos), 0), 80), 80, combine_color_brightness(self.right_color, 1))
                

        self.pos += self.step_size

        return self.array

class PatterGeneratorSwitch2(PatternGeneratorBase):
    def __init__(self, num_stripes, leds_per_stripe) -> None:
        super().__init__(num_stripes, leds_per_stripe)
        self.pos = 0
        self.step_size = 0

        self.beat_counter = 0

        self.left_colors = []
        self.right_colors = []

        for i in range(self.num_stripes):
            self.left_colors.append(self.color)
            self.right_colors.append(self.color)

        self.length_bar = 35

    def beat_trigger(self, time_until_next):
        self.step_size = get_step_size(time_until_next, self.length_bar, self.framerate)
        if self.beat_counter % 2 == 0:
            self.pos = 0

            if self.is_random_color():
                r = range(self.num_stripes)
                for i in r[::2]:
                    self.left_colors[i] = get_random_color_diff(self.left_colors[i])
                for i in r[1::2]:
                    self.right_colors[i] = get_random_color_diff(self.right_colors[i])
            else:
                r = range(self.num_stripes)
                for i in r[::2]:
                    self.left_colors[i] = self.color
                    self.right_colors[i] = self.color
        else:
            self.pos = self.length_bar
            self.step_size *= -1
            if self.is_random_color():
                r = range(self.num_stripes)
                for i in r[1::2]:
                    self.left_colors[i] = get_random_color_diff(self.left_colors[i])
                for i in r[::2]:
                    self.right_colors[i] = get_random_color_diff(self.right_colors[i])
            else:
                r = range(self.num_stripes)
                for i in r[1::2]:
                    self.left_colors[i] = self.color
                    self.right_colors[i] = self.color
        self.beat_counter += 1

    def next_frame(self, dt):
        self.reset_array()

        for y in range(self.num_stripes):
            if y % 2 == 0:
                # if x_pos < self.pos:
                self.fill_spot(y, 0, min(max(int(self.pos), 0), self.length_bar), combine_color_brightness(self.left_colors[y], 1))
                self.fill_spot(y, min(max(int(self.pos), 0), self.length_bar) + 80 - self.length_bar, 80, combine_color_brightness(self.right_colors[y], 1))
            else:
                # if x_pos > self.pos:
                self.fill_spot(y, 0, self.length_bar - min(max(int(self.pos), 0), self.length_bar), combine_color_brightness(self.left_colors[y], 1))
                self.fill_spot(y, 80 - min(max(int(self.pos), 0), self.length_bar), 80, combine_color_brightness(self.right_colors[y], 1))
                # self.fill_spot(y, 80 - self.length_bar - min(max(int(self.pos), 0), self.length_bar), 80, combine_color_brightness(self.right_color, 1))
                

        self.pos += self.step_size

        return self.array