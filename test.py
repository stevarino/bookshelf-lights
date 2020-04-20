import main
import unittest

class FakeStrand(object):
    def __init__(self, length):
        self.pixels = [(0, 0, 0)] * length
        self.length = length

    def __len__(self):
        return self.length

    def show(self):
        pass

    def __getitem__(self, item):
        return self.pixels[item]

    def __setitem__(self, item, value):
        self.pixels[item] = value

class FakeButton(object):
    def __init__(self, value=False):
        self.value = value

class CallbackCounter(object):
    def __init__(self):
        self.value = 0

    def __call__(self, *args, **kwargs):
        self.value += 1

    def __eq__(self, other):
        return other == self.value


def get_display(length):
    display = main.Display(FakeStrand(1), 1, 1)
    display.sleep = lambda: 'noop'
    return display



class TestDisplay(unittest.TestCase):
    def test_blink(self):
        """
        Adds Fade to a one pixel strand, ensures it updates the pixel and the
        pixel is updated with each tick.
        """
        display = get_display(1)
        display.register_state(main.Fade)
        prev = display.strand[0]
        for i in range(1000):
            display.tick()
            assert(all(0 <= display.strand[0][i] <= 255 for i in range(3)))
            assert display.strand[0] != prev
            prev = display.strand[0]

    def test_button(self):
        """
        Presses a button, ensuring the callback is called once.
        """
        callback = CallbackCounter()
        display = get_display(0)
        button = FakeButton()
        display.register_onpress(button, callback)
        assert callback == 0
        display.read()
        assert callback == 0
        button.value = True
        display.read()
        assert callback == 1
        for i in range(5):
            display.read()
        assert callback == 1
        

if __name__ == '__main__':
    unittest.main()
