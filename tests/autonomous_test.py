import network
import autonomous
from autonomous import Position, AutonomousRoutine, get_game_specific_message
from subsystems.drivetrain import Drivetrain
import os

def test_get_game_specific_message():
    assert get_game_specific_message("LLL") == Position.LEFT
    assert get_game_specific_message("LRL") == Position.LEFT
    assert get_game_specific_message("RLR") == Position.RIGHT
    assert get_game_specific_message("RRR") == Position.RIGHT


# These aren't really rigous tests, just ones mean as a spot check that
# they don't cause crashes.

def test_autonomous_routines():
    # These take a long time to run (about 15 seconds total), so we really only
    # want to run this on TravisCI.
    # According to https://docs.travis-ci.com/user/environment-variables/#Convenience-Variables
    # the environment variable "CI" along with others is set to True when we're in a
    # Travis environment.
    if os.environ.get("CI") == "true":
        drivetrain = MockDrivetrain()
        gyro = MockGyro()
        vision_socket = network.MockSocket()
        auton = autonomous.center_to_switch(drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        for _ in auton: pass
        auton = autonomous.switch_same_side(drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        for _ in auton: pass
        auton = autonomous.switch_opposite_side(drivetrain, gyro, vision_socket, autonomous.Position.LEFT)
        for _ in auton: pass

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
    auton = autonomous.VisionAuto(drivetrain, gyro, vision_socket, forward=0.5)
    for _ in range(0, 100):
        auton.run()

class MockGyro:
    def getAngle(self):
        return 180

class MockDrivetrain(Drivetrain):
    def __init__(self):
        pass

    def arcade_drive(self, forward, rotate):
        pass

    def stop(self):
        pass

    def shift_low(self):
        pass

    def shift_high(self):
        pass
