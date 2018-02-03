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
        self.init_angle = self.gyro.getAngle()
        self.angle = 0.0 # Scaled such that 360 -> 1.0

    def execute(self):
        while True:
            self.try_update_angle()
            self.drivetrain.arcade_drive(0.0, -self.angle)
            print(f"{-self.angle/2.0}")
            yield

    def try_update_angle(self):
        try:
            json = self.socket.get_packet()
            if json["sender"] == "vision":
                self.angle = json["angle"]/30.0
        except IOError as e:
            print(f"Couldn't update goal: {e}")




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
