import ctre
import wpilib
from wpilib.interfaces import GenericHID

import autonomous
import network
from autonomous import ArcadeAutonomous, RotateAutonomous
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.grabber import Grabber
from subsystems.wings import Wings

# Left and right sides for the Xbox Controller
# Note that these dont' referr to just the sticks, but more generally
# Refer to the left and right features of the controller.
# Ex: LEFT may refer to the actual left joystick, the left trigger,
# or left bumper.
LEFT = GenericHID.Hand.kLeft
RIGHT = GenericHID.Hand.kRight



ELEVATOR_ID = 6
LEFT_GRABBER_ID = 3 # TODO: Make sure this is the right ID
RIGHT_GRABBER_ID = 4 # TODO: Make sure this is the right ID

LEFT1_ID = 1
LEFT2_ID = 2
RIGHT1_ID = 7
RIGHT2_ID = 8

# 5 is not mapped currently to any motor

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
        self.drivetrain = Drivetrain(left, right, wpilib.DoubleSolenoid(2, 3))

        self.grabber = Grabber(
            ctre.WPI_TalonSRX(LEFT_GRABBER_ID),
            ctre.WPI_TalonSRX(RIGHT_GRABBER_ID),
            None,
        )

        self.elevator = Elevator(ctre.WPI_TalonSRX(ELEVATOR_ID))

        self.wings = Wings(
            wpilib.DoubleSolenoid(0, 1),
            wpilib.DoubleSolenoid(4, 5),
        )

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

        self.auto_exec = iter([])

        self.gyro = wpilib.ADXRS450_Gyro()

        self.vision_socket = network.VisionSocket()
        self.vision_socket.start()
        self.timer = 0

    def robotPeriodic(self):
        if self.timer % 100 == 0:
            print(self.vision_socket.get_angle(1.0))
            print("is bound: {}".format(self.vision_socket.is_bound()))
        self.timer += 1

    def teleopInit(self):
        print("Teleop Init Begin!")

    def teleopPeriodic(self):
        # @Todo: Deadzone these
        forward = -self.driver.getY(RIGHT)
        rotate = self.driver.getX(LEFT)

        if self.driver.getXButton():
            self.drivetrain.stop()
        else:
            self.drivetrain.arcade_drive(forward, rotate)

        gear_high = self.driver.getBumper(RIGHT)

        if gear_high:
            self.drivetrain.shift_high()
        else:
            self.drivetrain.shift_low()

        left_trigger = self.operator.getTriggerAxis(LEFT)
        right_trigger = self.operator.getTriggerAxis(RIGHT)

        TRIGGER_LEVEL = 0.4

        if abs(left_trigger) > TRIGGER_LEVEL:
            self.elevator.go_up(left_trigger)
        elif abs(right_trigger) > TRIGGER_LEVEL:
            self.elevator.go_down(right_trigger)
        else:
            self.elevator.stop()

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

        left_stick = self.operator.getY(LEFT)
        right_stick = self.operator.getY(RIGHT)
        # TRIGGER_LEVEL = 0.4
        self.grabber.set_left(left_stick)
        self.grabber.set_right(right_stick)
        # if right_trigger > TRIGGER_LEVEL and left_trigger > TRIGGER_LEVEL:
        #     self.grabber.spit(min(right_trigger, left_trigger))
        # elif right_trigger > TRIGGER_LEVEL or left_trigger > TRIGGER_LEVEL:
        #     self.grabber.absorb(max(right_trigger, left_trigger))



    def autonomousInit(self):
        print("Autonomous Begin!")
        self.auton = autonomous.drive_and_rotate(self.drivetrain, self.gyro)

    def autonomousPeriodic(self):
        try:
            next(self.auton)
        except StopIteration:
            # WPILib prints a ton of error messages when the motor has no output
            # send to it, so we stop the drivetrain to make it quiet. Also,
            # this ensures that we actually stop at the end of autonomous instead
            # of potentially running away for no reason.
            self.drivetrain.stop()

    # Close the socket when the main process ends.
    def __del__(self):
        self.vision_socket.close()


if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
