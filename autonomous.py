import math
import time
from enum import Enum

import wpilib

# In inches per second
ROBOT_SPEED = 9.0*12
ENCODER_TICKS_PER_FOOT = 830.0
ENCODER_TICKS_PER_INCH = ENCODER_TICKS_PER_FOOT / 12.0


# All measurements in inches unless specified

# robot in center
# WALL_TO_SWITCH = 11.0*12.0 # distance from the wall to the switch
CENTER_FORWARD_DIST = 6.0*12.0
CENTER_ROTATE_ANGLE = 30.0 # in degrees
CENTER_FORWARD_DIST_2 = 6.0*12.0

# robot on side, going to same side switch
SAME_SIDE_DIST = 14.0*12.0
SAME_SIDE_DIST_2 = 6.0
SAME_TURN_ANGLE = -90.0 # in degrees

# robot on side, going to far side switch
FAR_DIST_1 = 19.00 * 12.00 + 10.00
FAR_TURN_ANGLE = 90 # in degrees
FAR_DIST_2 = 13.0*12.0 + 4.0

# VisionAuto PID constants
VISION_P = 0.04
VISION_I = 0.00
VISION_D = 0.00

# Describes the position of the scales and switches
class Position(Enum):
    # Format is always our switch, scale, enemy side switch
    UNKNOWN = "Unknown" # Avoid selecting this!!! Set where the robot is!!!!
    LEFT = "Left"
    RIGHT = "Right"

# Defines which possible autonomi routines there are
class AutonomousRoutine(Enum):
    SWITCH = "robot on side, switch same side"
    SCALE = "robot on side, switch opposite side"
    AUTON_LINE = "breaking auto line only"
    ZIG_ZAG = "a ziggy boi"

'''
Determine which auton routine to run based on robot, switch, and scale positions
The robot will prioritize the scale over the switch when possible
If neither are possible, will attempt zigzag
If position is never set b/c dummies, will attempt an auton line crossing
'''
def get_routine(robot_position, switch_position, scale_position):
    if robot_position == Position.UNKNOWN:
        return AutonomousRoutine.AUTON_LINE
    elif robot_position == switch_position:
        return AutonomousRoutine.SWITCH
    elif robot_position == scale_position:
        return AutonomousRoutine.SCALE
    else:
        return AutonomousRoutine.ZIG_ZAG

'''Returns the switch and scale configurations'''
def get_game_specific_message(game_message):
    if game_message == "LLL":
        return (Position.LEFT, Position.LEFT)
    elif game_message == "LRL":
        return (Position.LEFT, Position.RIGHT)
    elif game_message == "RLR":
        return (Position.RIGHT, Position.LEFT)
    elif game_message == "RRR":
        return (Position.RIGHT, Position.RIGHT)
    else:
        # Is this a good idea?
        return (None, None)


def dead_reckon(drivetrain, gyro):
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=1.0, inches=135), duration = 3.5).run()  

def vision_reckon(drivetrain, gyro, vision_socket):
    yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, forward=0.6, look_for="retroreflective"), duration=5.0).run()

def eight_foot(grabber, elevator, drivetrain, gyro, vision_socket, switch_position):
    print("Begin EIGHT FOOT AUTON")
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.5, inches=12*8), duration=20.0).run()

# Used when the robot starts in the center, vision implemented
# Currently, vision is set at a hard limit of 5 seconds, which means we may drive into the switch a little bit (which is fine essentially)
# But having a "stop" of some sort would be nice
def center_straight(grabber, elevator, drivetrain, gyro, vision_socket, switch_position):
    print("BEGIN CENTER STRAIGHT AUTON")
    rotate = 45 if switch_position == Position.RIGHT else -45
    # yield from Timed(ElevatorAutonomous(elevator, up_speed=0.7), duration = 0.5).run()
    # print("ELEVATOR UP A LITTLE BIT")
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.7, inches=45), duration=10.0).run()
    print("End the first forward distance")
    #The angle below needs to be tuned to the field... if we have a gryo set it between 30-40 degrees
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=rotate, turn_speed=1), duration=1).run() 
    print("End first rotation")
    #This distance below must also be retested, this is not calibrated to field measurements
    distance = 35 if switch_position == Position.RIGHT else 45
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.7, inches=distance), duration=5.0).run()
    print("Go forward after first rotation")
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=-rotate, turn_speed=1), duration=1).run()
    print("End second rotation")
    yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, forward=0.5, look_for="retroreflective"), duration=6.0).run()
    print("Vision Autonomous Routine")
    yield from Timed(ElevatorAutonomous(elevator, up_speed=1), duration = 3.5).run()
    print("ELEVATOR UP A LITTLE BIT MORE")
    yield from Timed(GrabberAutonomous(grabber, in_speed=-1), duration=1).run()
    print("End grabber spit")


# Used when the switch is on the same side of the starting position. For
# example, when the robot starts on the left side and the switch is on the left side
def switch_to_same_side(grabber, elevator, drivetrain, gyro, vision_socket, switch_position):
    # grabber.set(-1)
    # rotate = SAME_TURN_ANGLE if switch_position == Position.LEFT else -SAME_TURN_ANGLE
    rotate = 90 if switch_position == Position.LEFT else -90
    # Makes the elevator go up at the same time as the first drive forward phase
    # yield from Timed(ElevatorAutonomous(elevator, up_speed=1), duration = 0.5).run()
    # print("end elevator")
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=1.0, inches=135), duration = 3.5).run()  
    yield from Timed(ArcadeAutonomous(drivetrain, forward=0, rotate=0), duration=0.3).run() # this is the STOP for when the cage comes down
    # yield from Timed(GrabberAutonomous(grabber, in_speed=0.3), duration = 0.3).run()    
    # yield from Timed(RotateAutonomous(drivetrain, gyro, angle=rotate, turn_speed=0.7), duration=2.5).run()
    yield from Timed(ElevatorAutonomous(elevator, up_speed=1), duration = 2.0).run() 
    yield from Timed(Parallel(
        RotateAutonomous(drivetrain, gyro, angle=rotate, turn_speed=0.7),
        GrabberAutonomous(grabber, in_speed=-0.25),
        ), duration=2.5).run()    
     
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.5, inches=24), duration = 1.5).run()
    yield from Timed(GrabberAutonomous(grabber, in_speed=1), duration=1).run()
    

def scale_to_same_side(grabber, elevator, drivetrain, gyro, vision_socket, scale_position):
    rotate = 90 if scale_position == Position.LEFT else -90
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=1, inches=275), duration=10.0).run()
    yield from Timed(Parallel(
        ElevatorAutonomous(elevator, up_speed=1),
        GrabberAutonomous(grabber, in_speed=-0.25)),
        duration=6).run()
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=rotate, turn_speed=0.7), duration=1.5).run()
    # yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.5, inches=10), duration = 1.5).run()
    yield from Timed(GrabberAutonomous(grabber, in_speed=1), duration=1).run()

def zig_zag(grabber, elevator, drivetrain, gyro, vision_socket, switch_position):
    rotate = -90 if switch_position == Position.LEFT else 90
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=1, inches=200), duration=10).run()
    yield from Timed(Parallel(
        RotateAutonomous(drivetrain, gyro, angle=rotate, turn_speed=0.7),
        GrabberAutonomous(grabber, in_speed=-0.30),
        ), duration=2.5).run()
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=1, inches=80), duration=10).run()
   

def scale_zig_zag(grabber, elevator, drivetrain, gyro, vision_socket, switch_position):
    rotate = 1 if switch_position == Position.LEFT else -1
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.7, inches=228.5), duration=10.0).run()
    yield from Timed(ArcadeAutonomous(drivetrain, forward=0, rotate=90), duration=0.75).run()
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.7, inches=120), duration=10.0).run()
    yield from Timed(RotateAutonomous(drivetrain, forward=0, rotate=-90), duration=0.75).run()
    yield from Timed(ElevatorAutonomous(elevator, up_speed=1), duration=3.5).run()
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.7, inches=65), duration=5).run()
    yield from Timed(GrabberAutonomous(grabber, in_speed=1), duration=1).run()

# Used when the switch is on the opposite side of the starting position. For
# example, when the robot starts on the left side but the switch is on the right side, zigzag

# def vision(drivetrain, gyro, vision_socket, forward, look_for):
#     yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, forward, look_for), duration = 30.0).run()

def zig_zag_encoder(grabber, elevator, drivetrain, gyro, vision_socket, switch_position):
    print("BEGIN ZIG ZAG ENCODER AUTON")
    rotate = 90 if switch_position == Position.RIGHT else -90
    # yield from Timed(ElevatorAutonomous(elevator, up_speed=0.7), duration = 0.5).run()
    # print("End elevator inital")
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.7, inches=200), duration=10).run()
    print("End the first forward distance")
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=rotate, turn_speed=1), duration=1).run()
    print("End first rotation right")
    yield from Timed(EncoderAutonomous(drivetrain, gyro=gyro, speed=0.7, inches=160), duration=10).run()
    print("End the second forward distance")
    yield from Timed(RotateAutonomous(drivetrain, gyro, angle=rotate, turn_speed=1), duration=1).run()
    print("End second rotation right")
    yield from Timed(ElevatorAutonomous(elevator, up_speed=1), duration = 2.0).run()
    print("End elevator final")
    yield from Timed(ArcadeAutonomous(drivetrain, forward=0.4, rotate=0), duration=1.5).run()
    print("End final distance forward")
    yield from Timed(GrabberAutonomous(grabber, in_speed=1), duration=1).run()
    print("End grabber")

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

    def end(self):
        self.auto.end()


class VisionAuto(BaseAutonomous):
    """
    Rotate the robot towards the target using incoming vision packets
    vision_socket is a VisionSocket, not a Python socket
    """
    def __init__(self, drivetrain, gyro, vision_socket, forward, look_for):
        """
        forward is from 0 to 1
        look_for is either "retroreflective", or "cube"
        """
        self.drivetrain = drivetrain
        self.socket = vision_socket
        self.gyro = gyro
        self.forward = forward
        self.correction = 0
        self.look_for = look_for
        # PID Constants, tuned as of March 5th
        self.PID = wpilib.PIDController(VISION_P, VISION_I, VISION_D,
            source=self._get_angle,
            output=self._set_correction)

        print("P: ", VISION_P)
        print("I: ", VISION_I)
        print("D: ", VISION_D)

    def _get_angle(self):
        angle = self.socket.get_angle(key=self.look_for, max_staleness=0.5)
        if angle is None:
            return 0
        return angle

    def _set_correction(self, value):
        self.correction = value

    def init(self):
        self.PID.setInputRange(-35, 35)
        self.PID.enable()

    def execute(self):
        # Values to make angle correction smaller:
        # ~57% = (x / 1.75)
        # ~47% = (x / 2.13)
        # ~42% = (x / 2.38)
        # ~30% = (x / 3.33)
        while True:
            angle = self.socket.get_angle(key=self.look_for, max_staleness=0.5)
            if angle is not None:
                correction = self.correction
                # print("self.Correction: ", self.correction)
                # print("Correction: ", correction)
                correction = math.copysign(self.correction, angle)
                self.drivetrain.arcade_drive(self.forward, correction)
            else:
                self.drivetrain.arcade_drive(self.forward, 0)
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
        self.start_angle = self.gyro.getYaw()

    def execute(self):
        while True:
            # We need the different between the goal angle delta and the current angle delta
            angle_error = abs(self.angle_goal) - abs(self.start_angle - self.gyro.getYaw())

            if angle_error < 1.0:
                print("BROKE EARLY")
                break

            correction_factor = angle_error / 10.0
            if correction_factor > 1.0:
                correction_factor = 1.0
            if self.angle_goal > 0:
                self.drivetrain.arcade_drive(0, self.speed * correction_factor)
            else:
                self.drivetrain.arcade_drive(0, -self.speed * correction_factor)
            if angle_error > 1:
                yield

    def end(self):
        self.drivetrain.stop()

'''
Drives the robot forward using the encoder
'''
class EncoderAutonomous(BaseAutonomous):
    def __init__(self, drivetrain, gyro, speed=0, inches=0):
        self.drivetrain = drivetrain
        self.distance = inches * ENCODER_TICKS_PER_INCH
        self.forward = speed
        self.gyro = gyro

    def init(self):
        self.start_dist = self.drivetrain.get_encoder_position()
        self.start_angle = self.gyro.getAngle()

    def execute(self):
        while abs(self.start_dist - self.drivetrain.get_encoder_position()) < self.distance:
            delta_angle = self.start_angle - self.gyro.getAngle()
            delta_rotate = 0
            delta_rotate = delta_angle/90.0
            print("delta ang", delta_angle, "delta_rotate", delta_rotate)
            if abs(self.start_dist - self.drivetrain.get_encoder_position()) > 0.9 * self.distance:
                self.drivetrain.arcade_drive(self.forward * 0.7, rotate=0)
            else:
                self.drivetrain.arcade_drive(self.forward, rotate=0)
            print("encoder dist", abs(self.start_dist - self.drivetrain.get_encoder_position()), "goal distance", self.distance)
            yield

    def end(self):
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

    def end(self):
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

    def end(self):
        self.elevator.stop()

class GrabberAutonomous(BaseAutonomous):
    """ Controls the cube manipulator during autonomous - SPIT OUT IS POSITIVE 1, SUCK IS NEGATIVE 1"""
    def __init__(self, grabber, in_speed=0):
        self.grabber = grabber
        self.in_speed = in_speed

    def execute(self):
        while True:
            self.grabber.set(self.in_speed)
            yield

    def end(self):
        self.grabber.set(0)

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
                    if self.exit_any:
                        running = False
            yield

    def end(self):
        for auto in self.autos:
            auto.end()

