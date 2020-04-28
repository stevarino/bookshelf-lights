import logging
import logging.handlers
import os
import subprocess
import time

LENGTH = 2
DELAY = 0.05

logger = logging.getLogger(__name__)

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
        self.high = 15
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
    def __init__(self, strand, delay):
        self.strand = strand
        self.states = []
        self.delay = delay
        self._button_handles = {}
        self._button_values = {}
        self._on_press = {}
        self._on_release = {}

        # repert every 5 minutes = 300s/report = 6000 ticks @ 0.05s/tick
        self.loop_limit = 300 / delay 
        self.loop_cnt = 0
        self.loop_total = 0
        self.loop_max = 0

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
            start = time.time()
            self.read()
            self.tick()
            self.strand.show()
            self.sleep(time.time() - start)

    def read(self):
        for btn, value in self._button_values.items():
            button = self._button_handles[btn]
            if not value and button.value:
                logger.info("button %s pressed", btn)
                self._button_values[btn] = True
                if btn in self._on_press:
                    self._on_press[btn]()
            elif value and not button.value:
                logger.info("button %s released", btn)
                self._button_values[btn] = False
                if btn in self._on_release:
                    self._on_release[btn]()

    def sleep(self, secs=0):
        self.loop_total += secs
        self.loop_cnt += 1
        if secs > self.loop_max:
            self.loop_max = secs
        if self.loop_cnt == self.loop_limit:
            logger.info("Time states: avg={:0.4f}s, max={:0.4f}s".format(
                self.loop_total / self.loop_limit,
                self.loop_max
            ))
            self.loop_cnt = 0
            self.loop_max = 0
            self.loop_total = 0
        if self.delay > secs:
            time.sleep(self.delay - secs)

    def tick(self):
        for state in self.states:
            state.tick()

            
    def register_onpress(self, pin, action):
        btn = str(pin)
        logger.info("Registered onpress for %s", btn)
        self._button_handles[btn] = pin
        self._button_values[btn] = False
        self._on_press[btn] = action

    def register_onrelease(self, pin, action):
        btn = str(pin)
        logger.info("Registered onrelease for %s", btn)
        self._button_handles[btn] = pin
        self._button_values[btn] = False
        self._on_release[btn] = action

    def clear(self):
        for i in range(len(self.strand)):
            self.strand[i] = (0, 0, 0)
        self.strand.show()


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
    import gpiozero
    import neopixel

    setup_logger()
    logger.info("Starting up... Strand length = %s, delay = %0.3f",
                LENGTH, DELAY)
 
    display = Display(neopixel.NeoPixel(board.D18, LENGTH), DELAY)

    def button_pressed(button_num):
        logger.info("button %s pressed", button_num)

    def shutdown():
        display.clear()
        subprocess.call('halt', shell=False)
 
    display.register_state(Fade, length=1)
    display.register_onpress(
        gpiozero.Button(4), shutdown)
    display.register_onpress(
        gpiozero.Button(17), lambda: button_pressed(2))
    try:
        display.loop()
    except BaseException as e:
        display.clear()
        logger.error("Error: %s", e.__class__.__name__, exc_info=True)

if __name__ == '__main__':
    main()
