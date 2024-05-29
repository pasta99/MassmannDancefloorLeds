import neopixel

class LEDDisplay:

    def __init__(self, pin, num_stripes, leds_per_stripe) -> None:
        self.pin = pin

    def show(self, array):
        print(array[0, 1])


class LEDDisplayReal(LEDDisplay):

    def __init__(self, pin, num_stripes, leds_per_stripe) -> None:
        self.pin = pin
        self.num_leds = num_stripes * leds_per_stripe

        ORDER = neopixel.GRBW
        self.pixels = neopixel.NeoPixel(self.pin, self.num_leds, brightness=0.01, pixel_order=ORDER, auto_write=False)

    def show(self, array):
        if not array.shape[0] * array.shape[1] == self.num_leds:
            print("Not right shape!")
            return 
        
        flattened_array = array.reshape(self.num_leds, 4)

        for i, c in enumerate(flattened_array):
            self.pixels[i] = (int(c[0] * c[3]), int(c[1] * c[3]), int(c[2] * c[3]), 0)

        self.pixels.show()

    def clear_all(self):
        self.pixels.fill((0, 0, 0, 0))

