import math
import time
from enum import Enum

import wpilib

# In inches per second
ROBOT_SPEED = 9.0*12
ENCODER_TICKS_PER_FOOT = 830.0
ENCODER_TICKS_PER_INCH = 830.0 / 12.0


# All measurements in inches unless specified

# robot in center
# WALL_TO_SWITCH = 11.0*12.0 # distance from the wall to the switch
CENTER_FORWARD_DIST = 6.0*12.0
CENTER_ROTATE_ANGLE = 30.0 # in degrees
CENTER_FORWARD_DIST_2 = 6.0*12.0

# robot on side, going to same side switch
SAME_SIDE_DIST = 14.0*12.0
SAME_TURN_ANGLE = -90.0 # in degrees

# robot on side, going to far side switch
FAR_VERTICAL_DIST = 19.00 * 12.00 + 10.00
FAR_TURN_ANGLE = 90 # in degrees
FAR_HORIZONTAL_DIST = 13.0*12.0 + 4.0
# Edit this to try out different autonomi
def test_auton(drivetrain, gyro, vision_socket, switch_position):
    # Chaining together autonomi is as simple as just adding more yield froms!
    yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, forward=0.7), duration=1).run()
    # yield from Timed(ArcadeAutonomous(drivetrain, forward=0.7, rotate=0), duration=1.5).run()
    # yield from Timed(RotateAutonomous(drivetrain, gyro, angle=45, turn_speed=0.6), duration=1).run()



# Describes the position of the scales and switches
class Position(Enum):
    # Format is always our switch, scale, enemy side switch
    LEFT = "Left"
    RIGHT = "Right"
    CENTER = "Center"

# Defines which possible autonomi routines there are
class AutonomousRoutine(Enum):
    CENTER = "robot in center"
    SIDE_TO_SAME = "robot on side, switch same side"
    SIDE_TO_OPPOSITE = "robot on side, switch opposite side"

def get_routine(robot_position, switch_position):
    if robot_position == Position.CENTER:
        return AutonomousRoutine.CENTER
    elif robot_position == switch_position:
        return AutonomousRoutine.SIDE_TO_SAME
    else:
        return AutonomousRoutine.SIDE_TO_OPPOSITE


'''Returns the switch and scale configurations'''
def get_game_specific_message(game_message):
    if game_message == "LLL":
        return Position.LEFT
    elif game_message == "LRL":
        return Position.LEFT
    elif game_message == "RLR":
        return Position.RIGHT
    elif game_message == "RRR":
        return Position.RIGHT
    else:
        # Is this a good idea?
        return None


# Used when the robot starts in the center
def center_straight(grabber, elevator, drivetrain, gyro, vision_socket, switch_position):
    self.grabber.set(1)
    # Makes the elevator go up at the same time as the first drive forward phase
    yield from Timed(Parallel(
            ElevatorAutonomous(elevator, up_speed=1.0),
            ArcadeAutonomous(drivetrain, forward=0.7, rotate=0),
        ), duration=2.0).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=45 * sign, turn_speed=0.6), duration=1).run()
    yield from Timed(ArcadeAutonomous(drivetrain, forward=0.7, rotate=0), duration=3).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=-50 * sign, turn_speed=0.6), duration=1).run()
    yield from Timed(ArcadeAutonomous(drivetrain, forward=0.7, rotate=0), duration=2).run() # TODO: Lower how far forward this goes
    yield from Timed(GrabberAutonomous(grabber, in_speed=-1), duration=1).run()
    self.grabber.set(0)
    # yield from VisionAuto(drivetrain, gyro, vision_socket, 0.5).run()

# Used when the switch is on the same side of the starting position. For
# example, when the robot starts on the left side and the switch is on the left side
def switch_to_same_side_left(drivetrain, gyro, vision_socket, switch_position):
    
    yield from Timed(EncoderAutonomous(drivetrain, forward = SAME_SIDE_DIST, speed = 0.7), duration = 3)
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle = -SAME_TURN_ANGLE, turn_speed=0.5), duration=1).run()
    yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, 0.6), duration=1).run()

# Used when switch is on the same side as the starting position, robot is on right and switch is on right    
def switch_to_same_side_right(drivetrain, gyro, vision_socket, switch_position):
    
    yield from Timed(EncoderAutonomous(drivetrain, forward = SAME_SIDE_DIST, speed = 0.7),duration = 3)
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle = SAME_TURN_ANGLE, turn_speed=0.5), duration=1).run()
    yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, 0.6), duration=1).run()

# Used when the switch is on the opposite side of the starting position. For
# example, when the robot starts on the left side but the switch is on the right side, zigzag
def zig_zag(drivetrain, gyro, vision_socket, switch_position):

    yield from Timed(ArcadeAutonomous(drivetrain, forward=0.7, rotate=0), duration=1.0).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=angle * sign, turn_speed=0.5), duration=1.0).run()
    yield from Timed(ArcadeAutonomous(drivetrain, forward=0.7, rotate=0), duration=1.0).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=angle * sign, turn_speed=0.5), duration=1.0).run()
    yield from Timed(ArcadeAutonomous(drivetrain, forward=0.3, rotate=0), duration=1.0).run()


def forward_with_vision(drivetrain, gyro, vision_socket, switch_position):
    yield from VisionAuto(drivetrain, gyro, vision_socket, duration=0.3).run()

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
    def __init__(self, auto, duration=0):
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

    def end(self):
        self.auto.end()


class VisionAuto(BaseAutonomous):
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
        # PID Constants, tuned as of March 5th
        self.PID = wpilib.PIDController(0.03, 0.01, 0.0,
            source=self._get_angle,
            output=self._set_correction)

    def _get_angle(self):
        angle = self.socket.get_angle(max_staleness=0.5)
        if angle is None:
            return 0
        return angle

    def _set_correction(self, value):
        self.correction = value

    def init(self):
        self.PID.setInputRange(-35, 35)
        self.PID.enable()

    def execute(self):
        while True:
            angle = self.socket.get_angle(max_staleness=0.5)
            if angle is not None:
                correction = self.correction
                # print("self.Correction: ", self.correction)
                print("Correction: ", correction)
                correction = math.copysign(self.correction, angle)/2.0
                self.drivetrain.arcade_drive(self.forward, correction)
            else:
                self.drivetrain.stop()
            yield

    def end(self):
        self.PID.disable()

class RotateAutonomous(BaseAutonomous):
    """
    Rotate the robot by the specified angle in degrees.
    Positive values will rotate clockwise, while negative values will rotate
    counterclockwise.
    """
    def __init__(self, drivetrain, gyro, angle=0, turn_speed=0):
        self.drivetrain = drivetrain
        self.gyro = gyro
        self.speed = turn_speed
        assert self.speed >= 0, "Speed ({}) must be positive!".format(self.speed)
        self.angle_goal = angle

    def init(self):
        self.start_angle = self.gyro.getAngle()

    def execute(self):
        while True:
            # We need the different between the goal angle delta and the current angle delta
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

'''
Drives the robot forward using the encoder
'''
class EncoderAutonomous(BaseAutonomous):
    def __init__(self, drivetrain, speed=0, inches=0):
        self.drivetrain = drivetrain
        self.distance = inches * ENCODER_TICKS_PER_INCH
        self.speed = speed

    def init(self):
        self.start_dist = self.drivetrain.get_encoder_position()

    def execute(self):
        while abs(self.start_dist - self.drivetrain.get_encoder_position()) < self.distance:
            self.drivetrain.arcade_drive(self.forward, rotate=0)

    def stop(self):
        self.drivetrain.stop()


class ArcadeAutonomous(BaseAutonomous):
    """
    Drive the robot as specified for the specific number of seconds
    duration is in seconds
    forward and rotate should be between and 1
    """

    def __init__(self, drivetrain, forward=0, rotate=0):
        self.drivetrain = drivetrain
        self.forward = forward
        self.rotate = rotate

    def execute(self):
        while True:
            self.drivetrain.arcade_drive(self.forward, self.rotate)
            yield

    def stop(self):
        self.drivetrain.stop()


class ElevatorAutonomous(BaseAutonomous):
    """ Controls the elevator during autonomous"""
    def __init__(self, elevator, up_speed=0):
        self.elevator = elevator
        self.up_speed = up_speed

    def execute(self):
        while True:
            self.elevator.go_up(self.up_speed)
            yield

    def stop(self):
        self.elevator.stop()

class GrabberAutonomous(BaseAutonomous):
    """ Controls the cube manipulator during autonomous"""
    def __init__(self, grabber, in_speed=0):
        self.grabber = grabber
        self.in_speed = in_speed

    def execute(self):
        while True:
            self.grabber.set(self.in_speed)
            yield

class Parallel(BaseAutonomous):
    def __init__(self, *autos, exit_any=False):
        self.autos = autos
        self.exit_any = exit_any

    def init(self):
        for auto in self.autos:
            auto.init()
        return self

    def execute(self):
        items = [auto.execute() for auto in self.autos]
        running = True
        while running:
            for item in items:
                try:
                    next(item)
                except StopIteration:
                    if exit_any:
                        running = False
            yield

    def stop(self):
        for auto in self.autos():
            auto.stop()

