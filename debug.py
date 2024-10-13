import board
import neopixel
import time

pixel_num  = 12 * 80
pixels = neopixel.NeoPixel(board.D18, pixel_num, brightness=.3, pixel_order=neopixel.GRB, auto_write=False)

pixels.fill((0, 0, 0))

pixels[0] = ((255, 0, 0))
pixels.show()

# def fill_color(color):
#     for i in range(pixel_num):
#         pixels[i] = color
#     pixels.show()

# fill_color((255, 0, 0))
# dt = 1/1000
# t = 0
# while True: 
#     fill_color((255, 0, 0))
#     time.sleep(dt)
#     fill_color((0, 0, 0))
#     time.sleep(dt)