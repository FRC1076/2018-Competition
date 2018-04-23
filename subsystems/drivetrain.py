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
    def __init__(self, left, right, gear_shifter, gyro, encoder_motor=None):
        self.encoder_motor = encoder_motor
        self.robot_drive = wpilib.drive.DifferentialDrive(left, right)
        self.gear_shifter = gear_shifter
        self.gyro = gyro

        self.setpoint = 0
        self.P = 1
        self.I = 0
        self.D = 0
        self.integral = 0
        self.prev_error = 0
        self.rcw = 0

    def setSetPoint(self, setpoint):
        self.setpoint = setpoint

    def PID(self):
        error = self.setpoint - self.gyro.getRate()
        self.integral = self.integral + (error * 0.05)
        derivative = (error -self.prev_error) / 0.05
        self.rcw = self.P * error + self.I * self.integral + self.D * derivative
        self.prev_error = error

    def arcade_drive(self, forward, rotate):
        if abs(rotate) < 0.2:
            self.robot_drive.arcadeDrive(-forward, rotate + self.rcw)
        else:
            self.robot_drive.arcadeDrive(-forward, rotate)
        self.setpoint = rotate * 9.0 # Experimentally determined that gyro.getRate outputs between +-9.0 usually

    def stop(self):
        self.robot_drive.stopMotor()

    def shift_low(self):
        self.gear_shifter.set(Drivetrain.LOW_GEAR)

    def shift_high(self):
        self.gear_shifter.set(Drivetrain.HIGH_GEAR)

    def get_encoder_position(self):
        return self.encoder_motor.getQuadraturePosition()

    def updatePID(self):
        self.PID()
        print("Correction: ", self.rcw, " | Setpoint:", self.setpoint, " | Gyro", self.gyro.getRate())