
import digitalio
import logging
import logging.handlers
import os
from time import sleep

import board
from gpiozero import Button
import neopixel


logger = logging.getLogger(__name__)
logger.info("Starting up...")

@dataclass
class State(object):
    """Abstract. Contains the state of a set of LEDs."""
    def __init__(self, strand, start, end):
        self.strand = strand
        self.start = start  # inclusive
        self.end = end  # exclusive
        self.setup()

    def setup():
        raise NotImplementedError()

    def tick():
        raise NotImplementedError()


class Fade(state):
    """Fades a range of LEDs on and off."""
    def setup():
        self.value = 0
        self.step = 1
        self.high = 255
        self.low = 0

    def tick():
        self.value += self.step
        if self.value > self.high:
            self.value = self.high - self.step
            self.step *= -1
        elif self.value < self.low:
            self.value = self.low - self.step
            self.step  *= -1

        for i in range(start, end):
            strand[i] = (state.value, 0, 0)


class Display(object):
    """Contains the state of the entire LED display."""
    def __init__(object, strand, length):
        self.strand = strand
        self.states = []

def setup_logger():
    logger.setLevel(logging.DEBUG)

    log_format = logging.Formatter(
    '%(asctime)s %(levelname)7s %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
    log_stream = logging.StreamHandler()
    log_stream.setFormatter(log_format)
    logging.getLogger().addHandler(log_stream)

    log_file = logging.handlers.TimedRotatingFileHandler(
    '/home/pi/logs/bookshelf-lights.log', when='d', backupCount=30)
    log_file.setFormatter(log_format)
    logging.getLogger().addHandler(log_file)

def setup_pins():
    pixels = neopixel.NeoPixel(board.D18, 1)
    button = Button(27)
    button.when_pressed = button_1_pressed
    button = Button(22)
    button.when_pressed = button_2_pressed

def button_1_pressed():
    logging.info("button 1 pressed")

def button_2_pressed():
    logging.info("button 2 pressed")

def main():
    delay = 0.01

    try:
        while True:
            loop()
            pixels.show()
            sleep(delay)
    except BaseException as e:
        logger.error("Error: %s", e.__class__.__name__, exc_info=True)

def loop():
    state = get_state('blinker', value=0, step=5, high=255, lo=0)
    i = 0
    j = 1
    hi = 255
    lo = 0

    pixels[0] = (state.value, 0, 0)
    i += j
    


pixels[0] = (0, 0, 0)
pixels.show()
