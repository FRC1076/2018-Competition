import ctre
import wpilib
from wpilib.interfaces import GenericHID

from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.grabber import Grabber
from subsystems.wings import Wings

from autonomous import ArcadeAutonomous

LEFT_STICK = GenericHID.Hand.kLeft
RIGHT_STICK = GenericHID.Hand.kRight


# @TODO: Actually have motor IDs for these
ELEVATOR_ID = 5
LEFT_GRABBER_ID = 6
RIGHT_GRABBER_ID = 7

# !! These are the motor IDs for the Purple robot!
# They may not be the correct ones for this year's competition robot
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

        left_grabber = ctre.WPI_TalonSRX(LEFT_GRABBER_ID)
        right_grabber = ctre.WPI_TalonSRX(RIGHT_GRABBER_ID)
        self.grabber = Grabber(left_grabber, right_grabber, None)

        self.elevator = Elevator(ctre.WPI_TalonSRX(ELEVATOR_ID))

        # @TODO: Do we even have latches?
        # @TODO: Find actual non-placeholder values for the channel IDs
        wings_left = wpilib.DoubleSolenoid(0, 1)
        wings_right = wpilib.DoubleSolenoid(2, 3)
        self.wings = Wings(wings_left, wings_right, None, None)

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

    def teleopInit(self):
        print()

    def teleopPeriodic(self):
        forward = self.driver.getY(RIGHT_STICK)
        rotate = self.driver.getX(LEFT_STICK)
        self.drivetrain.arcade_drive(forward, rotate)

    def autonomousInit(self):
        self.auton = ArcadeAutonomous(self.drivetrain, 0, 0.4, 1000)

    def autonomousPeriodic(self):
        self.auton.execute()


if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
