

class LEDDisplay:

    def __init__(self, pins) -> None:
        self.pins = pins

    def show(self, array):
        print(array[0, 0])