import board
import neopixel
from time import sleep
import digitalio

from gpiozero import Button

pixels = neopixel.NeoPixel(board.D18, 1)


i = 0
j = 5
hi = 255
lo = 0
delay = 0.05

pressed = False

def button_1_pressed():
  print("pressed")

button = Button(27)
button.when_pressed = button_1_pressed

try:
  while True:
    pixels[0] = (i, 0, 0)
    i += j
    if i > hi:
      print(hi)
      i = hi - j
      j *= -1
    elif i < lo:
      print(lo)
      i = lo - j
      j  *= -1
    pixels.show()
    sleep(delay)
except:
  pass

pixels[0] = (0, 0, 0)
pixels.show()
