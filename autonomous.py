import time
import math
import wpilib

def center_to_side(drivetrain, gyro, vision_socket):
    yield from RotateAutonomous(drivetrain, gyro, 45, 0.5).run()
    yield from ArcadeAutonomous(drivetrain, 0.3, 0, 3).run()
    yield from RotateAutonomous(drivetrain, gyro, 45, -0.5).run()
    yield from VisionAuto(drivetrain, gyro, vision_socket, 0.5).run()

def drive_and_rotate(drivetrain, gyro, vision_socket):
    yield from VisionAuto(drivetrain, gyro, vision_socket, 0.4).run()

class BaseAutonomous:
    def init(self):
        return self

    def execute(self):
        pass

    def end(self):
        pass


    def run(self):
        def _execute():
            yield from self.execute()
            self.end()
        self.init()
        return _execute()

class Timed:
    def __init__(self, auto, duration):
        self.auto = auto
        self.duration = duration

    def init(self):
        self.auto.init()
        self.end_time = time.time() + self.duration

    def execute(self):
        for _ in self.auto.execute():
            if time.time() > self.end_time:
                break
            yield


class VisionAuto:
    """
    Rotate the robot towards the target using incoming vision packets
    vision_socket is a VisionSocket, not a Python socket
    """
    def __init__(self, drivetrain, gyro, vision_socket, forward):
        self.drivetrain = drivetrain
        self.socket = vision_socket
        self.gyro = gyro
        self.forward = forward
        self.correction = 0
        self.PID = wpilib.PIDController(0.03, 0.0, 0.0,
            source=self._get_angle,
            output=self._set_correction)

    def _get_angle(self):
        angle = self.socket.get_angle(max_staleness=0.5)/30.0
        return angle

    def _set_correction(self, value):
        self.correction = value

    def init(self):
        self.PID.setInputRange(-35, 35)
        self.PID.enable()

    def init(self):
        # TODO: Use the gyro to better rotate to the target
        pass

    def execute(self):
        while True:
            angle = self.socket.get_angle(max_staleness=0.5)
            if angle is not None:
                correction = self.PID.get()
                correction = math.copysign(self.correction, angle)
                print("angle:{} correction: {}".format(angle, correction))
                self.drivetrain.arcade_drive(self.forward, correction)
            else:
                self.drivetrain.stop()
            yield

    def end(self):
        self.PID.disable()
        self.PID.free()

class RotateAutonomous(BaseAutonomous):
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
        assert speed >= 0, "Speed ({}) must be positive!".format(speed)

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


class ArcadeAutonomous(BaseAutonomous):
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
