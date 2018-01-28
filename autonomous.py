import time
import wpilib

def forward_auto(drivetrain):
    # Drive forward from the starting line to the switch
    # time?
    # speed?
    # figure those out in the function
    auto = ArcadeAutonomous(drivetrain, 1, 0, 3)
    auto.init()
    yield from auto.execute()

def chained_auto(drivetrain, gyro):
    print("Forward")
    auto1 = ArcadeAutonomous(drivetrain, 1, 0, 3)
    auto1.init()
    yield from auto1.execute()
    print("Rotate")
    auto2 = RotateAutonomous(drivetrain, gyro, 180, 0.5)
    auto2.init()
    yield from auto2.execute()
    print("Backwards")
    auto3 = ArcadeAutonomous(drivetrain, 1, 0, 3)
    auto3.init()
    yield from auto3.execute()
    print("End")

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

class RotateAutonomous:
    """
    Rotate the robot by the specified angle in degrees.
    Positive values will rotate clockwise, while negative values will rotate
    counterclockwise.
    """
    def __init__(self, drivetrain, gyro, angle, speed):
        self.drivetrain = drivetrain
        self.gyro = gyro
        self.speed = speed
        self.angle = angle
        assert speed > 0, "Speed ({}) must be positive!".format(speed)

    def init(self):
        self.start_angle = self.gyro.getAngle()
        # self.

    def execute(self):
        if self.angle > 0:
            while self.gyro.getAngle() - self.start_angle < self.angle:
                self.drivetrain.arcade_drive(0, self.speed)
                yield
        else:
            while self.gyro.getAngle() - self.start_angle > self.angle:
                self.drivetrain.arcade_drive(0, -self.speed)
                yield
        self.drivetrain.stop()

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
