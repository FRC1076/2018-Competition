import ctre
import wpilib
from wpilib.interfaces import GenericHID

from subsystems.drivetrain import Drivetrain

LEFT_STICK = GenericHID.Hand.kLeft
RIGHT_STICK = GenericHID.Hand.kRight


LEFT1_ID = 3
LEFT2_ID = 4
RIGHT1_ID = 1
RIGHT2_ID = 2

class Robot(wpilib.IterativeRobot):
    def robotInit(self):
        left1 = ctre.WPI_TalonSRX(LEFT1_ID)
        left2 = ctre.WPI_TalonSRX(LEFT2_ID)
        left = wpilib.SpeedControllerGroup(left1, left2)
        right1 = ctre.WPI_TalonSRX(RIGHT1_ID)
        right2 = ctre.WPI_TalonSRX(RIGHT2_ID)
        right = wpilib.SpeedControllerGroup(right1, right2)
        self.drivetrain = Drivetrain(left, right, None)


        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        forward = self.driver.getY(RIGHT_STICK)
        rotate = self.driver.getX(LEFT_STICK)
        self.drivetrain.arcade_drive(forward, rotate)

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass


if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
