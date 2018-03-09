import wpilib
import wpilib.drive
from wpilib import DoubleSolenoid

class Drivetrain:
    """
    The drivetrain class handles driving around as well as shifting between
    low and high gear
    """
    LOW_GEAR = DoubleSolenoid.Value.kReverse
    HIGH_GEAR = DoubleSolenoid.Value.kForward

    def __init__(self, left, right, gear_shifter):
        self.encoder_motor = left
        self.robot_drive = wpilib.drive.DifferentialDrive(left, right)
        self.gear_shifter = gear_shifter

    def arcade_drive(self, forward, rotate):
        self.robot_drive.arcadeDrive(forward, rotate)

    def stop(self):
        self.robot_drive.stopMotor()

    def shift_low(self):
        self.gear_shifter.set(Drivetrain.LOW_GEAR)

    def shift_high(self):
        self.gear_shifter.set(Drivetrain.HIGH_GEAR)

    def get_encoder_position():
        return self.encoder_motor.getQuadraturePosition()
