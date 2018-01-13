import wpilib


class Elevator:
    """
    The elevator will lift the grabber up and down to reach the cube.
    A motor will control a pulley/chain to bring it up or down.
    Limit switches will stop the motor when it gets too high or too low.
    """
    def __init__(self, motor):
        self.motor = motor

    def go_up(self, speed=1.0):
        pass

    def go_down(self, speed=1.0):
        pass
