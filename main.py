import board
import neopixel
from time import sleep
import digitalio
import logging
import logging.handlers

from gpiozero import Button

pixels = neopixel.NeoPixel(board.D18, 1)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter(
  '%(asctime)s %(levelname)7s %(name)s - %(message)s',
  datefmt='%Y%m%d %H%M%S')
log_stream = logging.StreamHandler()
log_stream.setFormatter(log_format)
logging.getLogger().addHandler(log_stream)

log_file = logging.handlers.TimedRotatingFileHandler(
  '/home/pi/logs/bookshelf-lights.log', when='d', backupCount=30)
log_file.setFormatter(log_format)
logging.getLogger().addHandler(log_file)




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

logger.info("Starting up...")
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
except BaseException as e:
  logger.error("Error: %s", e.__class__.__name__, exc_info=True)

pixels[0] = (0, 0, 0)
pixels.show()
