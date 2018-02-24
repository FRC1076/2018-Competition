import time
import math
import wpilib

def center_to_side(drivetrain, gyro, vision_socket, side):
    # angle = 45
    # sign = 1 if side == "R" else -1
    yield from Timed(ArcadeAutonomous(drivetrain, 0.7, 0), 1.5).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, -45, 0.6), 1).run()
    yield from Timed(ArcadeAutonomous(drivetrain, 0.7, 0), 3).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, 50, 0.6), 1).run()
    yield from Timed(ArcadeAutonomous(drivetrain, 0.7, 0), 2).run() # TODO: Lower how far forward this goes
    # yield from VisionAuto(drivetrain, gyro, vision_socket, 0.5).run()

def simple_forward(drivetrain, gyro, vision_socket, side):
    angle = 15
    sign = 1 if side == "L" else -1
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle * sign, 0.5), 1).run()
    yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, 0.6), 1).run()

def all_the_way_round(drivetrain, gyro, vision_socket, side):
    angle = 90
    sign = 1 if side == "L" else -1
    yield from Timed(ArcadeAutonomous(drivetrain, 0.7, 0, 4), 1.0).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle * sign, 0.5), 1.0).run()
    yield from Timed(ArcadeAutonomous(drivetrain, 0.7, 0, 4), 1.0).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle * sign, 0.5), 1.0).run()
    yield from Timed(ArcadeAutonomous(drivetrain, 0.3, 0, 2), 1.0).run()


def drive_and_rotate(drivetrain, gyro, vision_socket, side):
    yield from VisionAuto(drivetrain, gyro, vision_socket, 0.3).run()

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

class Timed(BaseAutonomous):
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
        assert speed >= 0, "Speed ({}) must be positive!".format(speed)
        self.angle_goal = angle

    def init(self):
        self.start_angle = self.gyro.getAngle()

    def execute(self):
        while True:
            angle_error = abs(self.angle_goal) - abs(self.start_angle - self.gyro.getAngle())
            correction_factor = angle_error / 10.0
            if correction_factor > 1.0:
                correction_factor = 1.0

            if self.angle_goal > 0:
                self.drivetrain.arcade_drive(0, self.speed * correction_factor)
            else:
                self.drivetrain.arcade_drive(0, -self.speed * correction_factor)
            yield

    def stop(self):
        self.drivetrain.stop()


class ArcadeAutonomous(BaseAutonomous):
    """
    Drive the robot as specified for the specific number of seconds
    duration is in seconds
    forward and rotate should be between and 1
    """

    def __init__(self, drivetrain, forward, rotate):
        self.drivetrain = drivetrain
        self.forward = forward
        self.rotate = rotate

    def execute(self):
        while True:
            self.drivetrain.arcade_drive(self.forward, self.rotate)
            yield

    def stop(self):
        self.drivetrain.stop()
