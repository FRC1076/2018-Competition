from wpilib import DoubleSolenoid

from helper import GetSet
from subsystems.drivetrain import Drivetrain


def test_forward():
    left_motor = GetSet(0)
    right_motor = GetSet(0)
    gyro = MockGyro()
    drivetrain = Drivetrain(left_motor, right_motor, None, gyro)
    drivetrain.arcade_drive(-0.69, 0)
    assert left_motor.state > 0
    assert right_motor.state < 0
    drivetrain.arcade_drive(0.69, 0)
    assert left_motor.state < 0
    assert right_motor.state > 0

def test_rotate():
    left_motor = GetSet(0)
    right_motor = GetSet(0)
    gyro = MockGyro()
    drivetrain = Drivetrain(left_motor, right_motor, None, gyro)
    drivetrain.arcade_drive(0, 0.42)
    assert left_motor.state > 0
    assert right_motor.state > 0
    drivetrain.arcade_drive(0, -0.42)
    assert left_motor.state < 0
    assert right_motor.state < 0


def test_gear_shifter():
    pneumatic = GetSet(Drivetrain.LOW_GEAR)
    gyro = MockGyro()
    drivetrain = Drivetrain(None, None, pneumatic, gyro)
    drivetrain.shift_high()
    assert pneumatic.state == Drivetrain.HIGH_GEAR
    drivetrain.shift_low()
    assert pneumatic.state ==  Drivetrain.LOW_GEAR

class MockGyro:
    def getYaw(self):
        return 180

    def getAngle(self):
        return 0

    def getRate(self):
        return 0
