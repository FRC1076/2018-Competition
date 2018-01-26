import time
import wpilib

class Timed:
    def __init__(self, auto, duration):
        self.auto = auto
        self.duration = duration

    def init(self):
        self.auto.init()
        self.end_time = time.time() + self.duration

    def execute(self):
        for _ in self.auto.execute():
            if time.time() > self.end_time():
                break
            yield

        auto_exec = self.auto.execute()
        while time.time() < self.end_time():
            try:
                next(auto_exec)
            except StopIteration:
                pass
            yield



class ArcadeAutonomous:
    """
    The elevator will lift the grabber up and down to reach the cube.
    A motor will control a pulley/chain to bring it up or down.
    Limit switches will stop the motor when it gets too high or too low.
    """

    def __init__(self, drivetrain, forward, rotate, duration):
        self.drivetrain = drivetrain
        self.forward = forward
        self.rotate = rotate
        self.duration = duration

    def init(self):
        self.end_time = time.time() + self.duration

    def execute(self):
        while time.time() < self.end_time:
            self.drivetrain.arcade_drive(self.forward, self.rotate)
            yield
        self.drivetrain.stop()
