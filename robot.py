import ctre
import wpilib
from wpilib.interfaces import GenericHID

from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.grabber import Grabber
from subsystems.wings import Wings

LEFT = GenericHID.Hand.kLeft
RIGHT = GenericHID.Hand.kRight

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

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        # @Todo: Deadzone these
        forward = self.driver.getY(RIGHT)
        rotate = self.driver.getX(LEFT)
        self.drivetrain.arcade_drive(forward, rotate)
        self.elevator.go_up(self.operator.getY(RIGHT))

        if self.operator.getPOV() != -1 and self.driver.getPOV() != -1:
            op_pov = self.operator.getPOV()
            driver_pov = self.driver.getPOV()
            left_wing_up = (
                (op_pov < 20 or 340 < op_pov) and
                (driver_pov < 20 or 340 < driver_pov)
            )
            left_wing_down = 160 < op_pov < 200 and 160 < driver_pov < 200
        else:
            left_wing_up = False
            left_wing_down = False

        right_wing_up = self.operator.getYButton() and self.driver.getYButton()
        right_wing_down = self.operator.getAButton() and self.driver.getAButton()

        if left_wing_up:
            self.wings.raise_left()
        if left_wing_down:
            self.wings.lower_left()
        if right_wing_up:
            self.wings.raise_right()
        if right_wing_down:
            self.wings.lower_right()

        left_trigger = self.operator.getTriggerAxis(LEFT)
        right_trigger = self.operator.getTriggerAxis(RIGHT)
        TRIGGER_LEVEL = 0.4
        if right_trigger > TRIGGER_LEVEL and left_trigger > TRIGGER_LEVEL:
            self.grabber.spit(min(right_trigger, left_trigger))
        elif right_trigger > TRIGGER_LEVEL or left_trigger > TRIGGER_LEVEL:
            self.grabber.absorb(max(right_trigger, left_trigger))


    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass


if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
