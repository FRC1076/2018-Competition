import ctre
import wpilib
from networktables import NetworkTables
from wpilib import DoubleSolenoid, SmartDashboard
from wpilib.interfaces import GenericHID

import autonomous
import network
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
        left1.setNeutralMode(ctre.NeutralMode.Brake)
        left2.setNeutralMode(ctre.NeutralMode.Brake)

        right1 = ctre.WPI_TalonSRX(RIGHT1_ID)
        right2 = ctre.WPI_TalonSRX(RIGHT2_ID)
        right = wpilib.SpeedControllerGroup(right1, right2)
        right1.setNeutralMode(ctre.NeutralMode.Brake)
        right2.setNeutralMode(ctre.NeutralMode.Brake)


        self.drivetrain = Drivetrain(left, right, None)

        self.grabber = Grabber(
            ctre.WPI_TalonSRX(LEFT_GRABBER_ID),
            ctre.WPI_TalonSRX(RIGHT_GRABBER_ID),
            None,
        )

        self.elevator = Elevator(ctre.WPI_TalonSRX(ELEVATOR_ID))

        # @TODO: Find actual non-placeholder values for the channel IDs
        self.wings = Wings(
            wpilib.DoubleSolenoid(2, 3),
            wpilib.DoubleSolenoid(4, 5),
        )

        self.brake = wpilib.DoubleSolenoid(0, 1)

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

        self.auto_exec = iter([])

        self.gyro = wpilib.ADXRS450_Gyro()

        # Use a mock socket in tests instead of a real one because we can't
        # actually bind to a port when testing the code.
        if Robot.isReal():
            self.vision_socket = network.VisionSocket()
        else:
            self.vision_socket = network.MockSocket()

        self.vision_socket.start()
        self.timer = 0

        self.sd = NetworkTables.getTable('SmartDashboard')

        self.chooser = wpilib.SendableChooser()
        self.chooser.addObject('left', 'left')
        self.chooser.addObject('right', 'right')
        self.chooser.addObject('center', 'center')

        SmartDashboard.putData("side_selector", self.chooser)

    def robotPeriodic(self):
        if self.timer % 1000 == 0:
            print(self.vision_socket.get_angle(1.0))
            print("ID: {}".format(self.vision_socket.get_id()))
            print("is bound: {}".format(self.vision_socket.is_bound()))
            print("choosen: ", self.chooser.getSelected())
        self.timer += 1

    def teleopInit(self):
        print("Teleop Init Begin!")

    def teleopPeriodic(self):
        # @Todo: Deadzone these
        forward = self.driver.getY(RIGHT)
        rotate = self.driver.getX(LEFT)

        if self.driver.getXButton():
            self.drivetrain.stop()
        else:
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
            self.brake.set(DoubleSolenoid.Value.kReverse)
        if left_wing_down:
            self.wings.lower_left()
            self.brake.set(DoubleSolenoid.Value.kForward)
        if right_wing_up:
            self.wings.raise_right()
            self.brake.set(DoubleSolenoid.Value.kReverse)
        if right_wing_down:
            self.wings.lower_right()
            self.brake.set(DoubleSolenoid.Value.kForward)

        left_trigger = self.operator.getTriggerAxis(LEFT)
        right_trigger = self.operator.getTriggerAxis(RIGHT)
        TRIGGER_LEVEL = 0.4
        if right_trigger > TRIGGER_LEVEL and left_trigger > TRIGGER_LEVEL:
            self.grabber.spit(min(right_trigger, left_trigger))
        elif right_trigger > TRIGGER_LEVEL or left_trigger > TRIGGER_LEVEL:
            self.grabber.absorb(max(right_trigger, left_trigger))

    def autonomousInit(self):
        print("Autonomous Begin!")
        # The game specific message is only given once autonomous starts
        # It is not avaliable during disable mode before the game starts
        # and it is not useful in teleop mode, so we only get the message here.
        game_message = wpilib.DriverStation.getInstance().getGameSpecificMessage()
        switch_position = autonomous.get_game_specific_message(game_message)
        robot_position = autonomous.Position.CENTER # TODO: have an actual way to set this outside of the program
        routine = autonomous.get_routine(robot_position=robot_position, switch_position=switch_position)
        print("Switch Position: ", switch_position)

        if routine == autonomous.AutonomousRoutine.CENTER:
            self.auton = autonomous.center_to_switch(self.drivetrain, self.gyro, self.vision_socket, switch_position)
        elif routine == autonomous.AutonomousRoutine.SIDE_TO_SAME:
            self.auton = autonomous.switch_same_side(self.drivetrain, self.gyro, self.vision_socket, switch_position)
        elif routine == autonomous.AutonomousRoutine.SIDE_TO_OPPOSITE:
            self.auton = autonomous.switch_opposite_side(self.drivetrain, self.gyro, self.vision_socket, switch_position)
        else:
            # Default to the center autonomous
            self.auton = autonomous.center_to_switch(self.drivetrain, self.gyro, self.vision_socket, switch_position)


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
