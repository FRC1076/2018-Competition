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


class VisionAuto:
    """
    Rotate the robot towards the target using incoming vision packets
    vision_socket is a VisionSocket, not a Python socket
    """
    def __init__(self, drivetrain, vision_socket, gyro):
        self.drivetrain = drivetrain
        self.socket = vision_socket
        self.gyro = gyro

    def init(self):
        # TODO: Use the gyro to better rotate to the target
        pass

    def execute(self):
        while True:
            angle = self.socket.get_angle(0.1) # Angle must be at most 0.1s old
            if angle is not None:
                self.drivetrain.arcade_drive(0.0, -angle/30.0)
            else:
                self.drivetrain.stop()
            print(f"{angle}")
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
        assert speed >= 0, f"Speed ({speed}) must be positive!"

    def init(self):
        self.start_angle = self.gyro.getAngle()

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
    Drive the robot as specified for the specific number of seconds
    duration is in seconds
    forward and rotate should be between and 1
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
