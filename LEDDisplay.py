import neopixel

class LEDDisplay:

    def __init__(self, pin, num_stripes, leds_per_stripe) -> None:
        self.pin = pin

    def show(self, array):
        print(array[0, 1])


class LEDDisplayReal(LEDDisplay):

    def __init__(self, pin, num_stripes, leds_per_stripe, brightness) -> None:
        self.pin = pin
        self.num_leds = num_stripes * leds_per_stripe
        self.brightness = brightness

        ORDER = neopixel.GRB
        self.pixels = neopixel.NeoPixel(self.pin, self.num_leds, brightness=1, pixel_order=ORDER, auto_write=False)

    def show(self, array, strobo=False):
        if not array.shape[0] * array.shape[1] == self.num_leds:
            print("Not right shape!")
            return 
        
        flattened_array = array.reshape(self.num_leds, 4)
        
        b = 1 if strobo else self.brightness

        for i, c in enumerate(flattened_array):
            self.pixels[i] = (int(c[0] * c[3] * b), int(c[2] * c[3] * b), int(c[1] * c[3] * b))

        self.pixels.show()

    def clear_all(self):
        self.pixels.fill((0, 0, 0))

    def set_brighness(self, brightness):
        self.brightness = brightness

