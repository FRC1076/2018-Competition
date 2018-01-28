import ctre
import wpilib
from wpilib.interfaces import GenericHID

from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.grabber import Grabber
from subsystems.wings import Wings

LEFT_STICK = GenericHID.Hand.kLeft
RIGHT_STICK = GenericHID.Hand.kRight
LEFT_BUMPER = GenericHID.Hand.kLeft
RIGHT_BUMPER = GenericHID.Hand.kRight

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
        self.wing_mode = False

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        forward = self.driver.getY(RIGHT_STICK)
        rotate = self.driver.getX(LEFT_STICK)
        self.drivetrain.arcade_drive(forward, rotate)
        self.elevator.go_up(self.operator.getY(RIGHT_STICK))
        
        left_trigger = self.operator.getTriggerAxis(LEFT_STICK)
        right_trigger = self.operator.getTriggerAxis(RIGHT_STICK)
        operator_safety = self.operator.getAButton() and self.operator.getBButton()
        driver_safety = self.driver.getAButton() and self.driver.getBButton()
        left_bumper = self.operator.getBumper(LEFT_BUMPER)
        right_bumper = self.operator.getBumper(RIGHT_BUMPER)
        
        TRIGGER_LEVEL = 0.4
        if operator_safety and driver_safety:
            wing_mode = True
        
        if wing_mode:
            if left_trigger > TRIGGER_LEVEL:
                self.wings.raise_left()
            if right_trigger > TRIGGER_LEVEL:
                self.wings.raise_right()
            if operator_safety:
                if left_bumper:
                    self.wings.lower_left()
                if right_bumper:
                    self.wings.lower_right()
        else:
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
