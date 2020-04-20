import logging
import logging.handlers
import os
import time


logger = logging.getLogger(__name__)
logger.info("Starting up...")

class State(object):
    """Abstract. Contains the state of a set of LEDs."""
    def __init__(self, strand, start, end):
        self.strand = strand
        self.start = start  # inclusive
        self.end = end  # exclusive
        self.setup()

    def setup(self):
        raise NotImplementedError()

    def tick(self):
        raise NotImplementedError()


class Fade(State):
    """Fades a range of LEDs on and off."""
    def setup(self):
        self.value = 0
        self.step = 1
        self.high = 255
        self.low = 0

    def tick(self):
        self.value += self.step
        if self.value > self.high:
            self.value = self.high - self.step
            self.step *= -1
        elif self.value < self.low:
            self.value = self.low - self.step
            self.step  *= -1

        for i in range(self.start, self.end):
            self.strand[i] = (self.value, 0, 0)


class Display(object):
    """Contains the state of the entire LED display."""
    def __init__(self, strand, length, delay):
        self.strand = strand
        self.states = []
        self.delay = delay
        self._button_values = {}
        self._on_press = {}
        self._on_release = {}

    def register_state(self, state_cls, length=0, index=-1):
        if index != -1:
            if index > len(self.states):
                raise ValueError("Invalid index: {} exceeds {}".format(
                    index, len(self.states)))
            self.states = self.states[0:index]
        start = 0
        if self.states:
            start = self.states[-1].end
        if start >= len(self.strand):
            raise ValueError("Invalid start: {} >= {}".format(
                start, len(self.strand)))
        if length == 0:
            length = len(self.strand) - start
        self.states.append(state_cls(self.strand, start, start + length))



    def loop(self):
        while True:
            self.read()
            self.tick()
            self.strand.show()
            self.sleep()

    def read(self):
        for button, value in self._button_values.items():
            if not value and button.value:
                self._button_values[button] = True
                if button in self._on_press:
                    self._on_press[button]()
            elif value and not button.value:
                self._button_values[button] = False
                if button.pin in self._on_release:
                    self._on_release[button.pin]()

    def sleep(self):
        sleep(self.delay)

    def tick(self):
        for state in self.states:
            state.tick()

            
    def register_onpress(self, pin, action):
        self._button_values[pin] = False
        self._on_press[pin] = action

    def register_onrelease(self, pin, action):
        self._button_values[pin] = False
        self._on_release[pin] = action


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


def main():
    import board
    import neopixel

    setup_logger()
    LENGTH = 1
    DELAY = 0.01
    def button_pressed(button_num):
        logging.info("button %s pressed", button_num)
 
    display = Display(neopixel.NeoPixel(board.D18, LENGTH), LENGTH, DELAY)
    display.register_state(Fade, length=1)
    display.register_state(Fade, length=1)
    display.register_onpress(board.D27, lambda: button_pressed(1))
    display.register_onpress(board.D22, lambda: button_pressed(2))
    try:
        display.loop()
    except BaseException as e:
        logger.error("Error: %s", e.__class__.__name__, exc_info=True)

if __name__ == '__main__':
    main()
