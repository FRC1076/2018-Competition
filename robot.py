import ctre
import wpilib
from wpilib.interfaces import GenericHID

from autonomous import ArcadeAutonomous
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.grabber import Grabber
from subsystems.wings import Wings

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
        left = wpilib.SpeedControllerGroup(
            ctre.WPI_TalonSRX(LEFT1_ID),
            ctre.WPI_TalonSRX(LEFT2_ID),
        )
        right = wpilib.SpeedControllerGroup(
            ctre.WPI_TalonSRX(RIGHT1_ID),
            ctre.WPI_TalonSRX(RIGHT2_ID),
        )
        self.drivetrain = Drivetrain(left, right, None)

        self.grabber = Grabber(
            ctre.WPI_TalonSRX(LEFT_GRABBER_ID),
            ctre.WPI_TalonSRX(RIGHT_GRABBER_ID),
            None,
        )

        self.elevator = Elevator(ctre.WPI_TalonSRX(ELEVATOR_ID))

        # @TODO: Do we even have latches?
        # @TODO: Find actual non-placeholder values for the channel IDs
        self.wings = Wings(
            wpilib.DoubleSolenoid(0, 1),
            wpilib.DoubleSolenoid(2, 3),
            None, None,
        )

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

        self.auto_exec = iter([])

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        forward = self.driver.getY(RIGHT_STICK)
        rotate = self.driver.getX(LEFT_STICK)
        self.drivetrain.arcade_drive(forward, rotate)

    def autonomousInit(self):
        self.auton = ArcadeAutonomous(self.drivetrain, 0, 0.4, 1)
        self.auton.init()
        self.auton_exec = self.auton.execute()

    def autonomousPeriodic(self):
        try:
            next(self.auton_exec)
        except StopIteration:
            # WPILib prints a ton of error messages when the motor has no output
            # send to it, so we stop the drivetrain to make it quiet. Also,
            # this ensures that we actually stop at the end of autonomous instead
            # of potentially running away for no reason.
            self.drivetrain.stop()


if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
