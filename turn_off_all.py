import board
import neopixel
pixels = neopixel.NeoPixel(board.D18, 100, brightness=0.0, pixel_order=neopixel.GRBW)

pixels.fill((0, 0, 0, 0))
pixels.show()