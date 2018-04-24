import network
import autonomous
from autonomous import Position, AutonomousRoutine, get_routine, get_game_specific_message
from subsystems.drivetrain import Drivetrain
import os

def test_get_game_specific_message():
    assert get_game_specific_message("LLL") == (Position.LEFT, Position.LEFT)
    assert get_game_specific_message("LRL") == (Position.LEFT, Position.RIGHT)
    assert get_game_specific_message("RLR") == (Position.RIGHT, Position.LEFT)
    assert get_game_specific_message("RRR") == (Position.RIGHT, Position.RIGHT)


def test_routine():
    assert get_routine(Position.LEFT, Position.LEFT, Position.LEFT) == AutonomousRoutine.SCALE
    assert get_routine(Position.LEFT, Position.LEFT, Position.RIGHT) == AutonomousRoutine.SWITCH
    assert get_routine(Position.LEFT, Position.RIGHT, Position.LEFT) == AutonomousRoutine.SCALE
    assert get_routine(Position.LEFT, Position.RIGHT, Position.RIGHT) == AutonomousRoutine.ZIG_ZAG

    assert get_routine(Position.RIGHT, Position.LEFT, Position.LEFT) == AutonomousRoutine.ZIG_ZAG
    assert get_routine(Position.RIGHT, Position.LEFT, Position.RIGHT) == AutonomousRoutine.SCALE
    assert get_routine(Position.RIGHT, Position.RIGHT, Position.LEFT) == AutonomousRoutine.SWITCH
    assert get_routine(Position.RIGHT, Position.RIGHT, Position.RIGHT) == AutonomousRoutine.SCALE


# These aren't really rigous tests, just ones mean as a spot check that
# they don't cause crashes.

def test_zig_zag():
    # These take a long time to run (about 15 seconds total), so we really only
    # want to run this on TravisCI.
    # According to https://docs.travis-ci.com/user/environment-variables/#Convenience-Variables
    # the environment variable "CI" along with others is set to True when we're in a
    # Travis environment.
    if os.environ.get("CI") == "true":
        drivetrain = MockDrivetrain()
        gyro = MockGyro()
        vision_socket = network.MockSocket()
        grabber = MockGrabber()
        elevator = MockElevator()
        auton = autonomous.zig_zag(grabber, elevator, drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        for _ in auton: drivetrain.position += 1

def test_center_straight():
    if os.environ.get("CI") == "true":
        drivetrain = MockDrivetrain()
        gyro = MockGyro()
        vision_socket = network.MockSocket()
        grabber = MockGrabber()
        elevator = MockElevator()
        auton = autonomous.center_straight(grabber, elevator, drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        for _ in auton: drivetrain.position += 1

def test_switch_to_same_side():
    if os.environ.get("CI") == "true":
        drivetrain = MockDrivetrain()
        gyro = MockGyro()
        vision_socket = network.MockSocket()
        grabber = MockGrabber()
        elevator = MockElevator()
        auton = autonomous.switch_to_same_side(grabber, elevator, drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        for _ in auton: drivetrain.position += 1

        # auton = autonomous.center_straight(grabber, elevator, drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        # for _ in auton: drivetrain.position += 1
        # auton = autonomous.switch_to_same_side_left(grabber, elevator, drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        # for _ in auton: drivetrain.position += 1
        # auton = autonomous.switch_to_same_side_right(grabber, elevator, drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        # for _ in auton: drivetrain.position += 1

def test_encoder_autonomous():
    drivetrain = MockDrivetrain()
    gyro = MockGyro()
    auton = autonomous.EncoderAutonomous(drivetrain, gyro=gyro, speed=0.42, inches=1.0)
    auton.init()
    for _ in range(0, 100):
        auton.run()
    auton.end()

def test_arcade_autonomous():
    drivetrain = MockDrivetrain()
    auton = autonomous.ArcadeAutonomous(drivetrain, forward=-0.42, rotate=0.69)
    for _ in range(0, 100):
        auton.run()


def test_rotate_autonomous():
    drivetrain = MockDrivetrain()
    gyro = MockGyro()
    auton = autonomous.RotateAutonomous(drivetrain, gyro, angle=90, turn_speed=0.5)
    for _ in range(0, 100):
        auton.run()


def test_vision_autonomous():
    drivetrain = MockDrivetrain()
    gyro = MockGyro()
    vision_socket = network.MockSocket()
    auton = autonomous.VisionAuto(drivetrain, gyro, vision_socket, forward=0.5, look_for="a_thing")
    for _ in range(0, 100):
        auton.run()

class MockGyro:
    def getYaw(self):
        return 180

    def getAngle(self):
        return 0

class MockDrivetrain(Drivetrain):
    def __init__(self):
        self.position = 0

    def arcade_drive(self, forward, rotate):
        pass

    def stop(self):
        pass

    def shift_low(self):
        pass

    def shift_high(self):
        pass

    def get_encoder_position(self):
        return self.position

class MockElevator:
    def __init__(self):
        pass

    def go_up(self, speed=1.0):
        pass

    def go_down(self, speed=1.0):
        pass

    def stop(self):
        pass

import wpilib

class MockGrabber:
    def __init__(self):
        pass

    def set(self, speed=1.0):
        pass

    def set_left(self, speed=1.0):
        pass

    def set_right(self, speed=1.0):
        pass

    def has_cube(self):
        pass
