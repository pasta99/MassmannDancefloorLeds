import board
import neopixel
import time

pixel_num  = 12 * 80
pixels = neopixel.NeoPixel(board.D18, pixel_num, brightness=.3, pixel_order=neopixel.GRB)

pixels.fill((0, 0, 0))