import autonomous
import ctre
import network
import robotpy_ext.common_drivers.navx as navx
import wpilib
from networktables import NetworkTables
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.grabber import Grabber
from subsystems.wings import Wings
from wpilib import DoubleSolenoid, SmartDashboard
from wpilib.interfaces import GenericHID

# Left and right sides for the Xbox Controller
# Note that these dont' referr to just the sticks, but more generally
# Refer to the left and right features of the controller.
# Ex: LEFT may refer to the actual left joystick, the left trigger,
# or left bumper.
LEFT = GenericHID.Hand.kLeft
RIGHT = GenericHID.Hand.kRight


ELEVATOR_ID = 6
LEFT_GRABBER_ID = 4
RIGHT_GRABBER_ID = 3

LEFT1_ID = 1
LEFT2_ID = 2
RIGHT1_ID = 7
RIGHT2_ID = 8

# 5 is not mapped currently to any motor

# Wing Solenoid IDs
LEFT_RETRACT = 0
LEFT_CENTER_EXTEND = 1
LEFT_OUTER_EXTEND = 2
RIGHT_RETRACT = 7
RIGHT_CENTER_EXTEND = 6
RIGHT_OUTER_EXTEND = 5

# If you modify this key, also update the value in index.html!
SIDE_SELECTOR = "side_selector"

class Robot(wpilib.IterativeRobot):
    def robotInit(self):
        self.left1 = ctre.WPI_TalonSRX(LEFT1_ID)
        self.left2 = ctre.WPI_TalonSRX(LEFT2_ID)
        left = wpilib.SpeedControllerGroup(self.left1, self.left2)

        self.right1 = ctre.WPI_TalonSRX(RIGHT1_ID)
        self.right2 = ctre.WPI_TalonSRX(RIGHT2_ID)
        right = wpilib.SpeedControllerGroup(self.right1, self.right2)

        self.drivetrain = Drivetrain(left, right, wpilib.DoubleSolenoid(3, 4), encoder_motor=self.left1)

        self.grabber = Grabber(
            ctre.WPI_TalonSRX(LEFT_GRABBER_ID),
            ctre.WPI_TalonSRX(RIGHT_GRABBER_ID),
            None,
        )

        self.elevator = Elevator(ctre.WPI_TalonSRX(ELEVATOR_ID))

        self.wings = Wings(
            left_retract=wpilib.Solenoid(LEFT_RETRACT),
            right_retract=wpilib.Solenoid(RIGHT_RETRACT),
            left_out_extend=wpilib.Solenoid(LEFT_OUTER_EXTEND),
            right_out_extend=wpilib.Solenoid(RIGHT_OUTER_EXTEND),
            left_center_extend=wpilib.Solenoid(LEFT_CENTER_EXTEND),
            right_center_extend=wpilib.Solenoid(RIGHT_CENTER_EXTEND),
        )

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

        self.auto_exec = iter([])

        # self.gyro = wpilib.ADXRS450_Gyro()
        self.gyro = navx.ahrs.AHRS.create_spi()

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
        self.chooser.addObject('left', autonomous.Position.LEFT)
        self.chooser.addObject('right', autonomous.Position.RIGHT)
        self.chooser.addObject('center', autonomous.Position.CENTER)
        SmartDashboard.putData(SIDE_SELECTOR, self.chooser)

    def robotPeriodic(self):
        if self.timer % 100 == 0:
            print(self.vision_socket.debug())
            # print('pitch ', self.gyro.getPitch())
            # print('yaw ', self.gyro.getYaw())
            # print('roll ', self.gyro.getRoll())
            # print("is bound: ", self.vision_socket.is_bound())
            # print("choosen: ", self.chooser.getSelected())
            # game_message = wpilib.DriverStation.getInstance().getGameSpecificMessage()
            # print("game msg: ", autonomous.get_game_specific_message(game_message))
            # print("routine: ", autonomous.get_routine(self.chooser.getSelected(), autonomous.get_game_specific_message(game_message)))
        self.timer += 1

    def teleopInit(self):
        self.left_activated = False
        self.right_activated = False
        print("Teleop Init Begin!")

    def teleopPeriodic(self):
        # Arcade Driver Controlls
        DEADZONE = 0.1
        forward = -self.driver.getY(RIGHT)
        rotate = self.driver.getX(LEFT)

        MAX_FORWARD = 0.9
        MAX_ROTATE = 1.0

        forward = deadzone(forward * MAX_FORWARD, DEADZONE)
        rotate = deadzone(rotate * MAX_ROTATE, DEADZONE)

        # Brake Button
        if self.driver.getXButton():
            self.drivetrain.stop()
        else:
            self.drivetrain.arcade_drive(forward, rotate)

        # Gear shifter, held = high gear
        gear_high = self.driver.getBumper(RIGHT)

        if gear_high:
            self.drivetrain.shift_low()
        else:
            self.drivetrain.shift_high()

        # Elevator Controllers
        # When the operator holds the trigger buttons, the elevator will move up and down
        left_trigger = self.operator.getTriggerAxis(LEFT)
        right_trigger = self.operator.getTriggerAxis(RIGHT)

        TRIGGER_LEVEL = 0.4

        if abs(left_trigger) > TRIGGER_LEVEL:
            self.elevator.go_up(left_trigger)
        elif abs(right_trigger) > TRIGGER_LEVEL:
            self.elevator.go_down(right_trigger)
        else:
            self.elevator.stop()

        # Wing Activations
        # Wings will activate when BOTH operator and driver hold Start (right wings)
        # or Select (left wings). After activation, control of the wings transfers exclusively to
        # the operator for control.

        # Note that the back button may also be called the select button depending on controller
        activate_left = self.operator.getBackButton() and self.driver.getBackButton()
        activate_right = self.operator.getStartButton() and self.driver.getStartButton()

        activate_left_released = self.operator.getBackButtonReleased() or self.driver.getBackButtonReleased()
        activate_right_released = self.operator.getStartButtonReleased() or self.driver.getStartButtonReleased()

        if activate_left:
            self.wings.raise_center_left()
        if activate_right:
            self.wings.raise_center_right()
        if activate_left_released:
            self.wings.lower_left()
            self.left_activated = True
        if activate_right_released:
            self.wings.lower_right()
            self.right_activated = True

        # Wing Controls
        if self.operator.getPOV() != -1:
            op_pov = self.operator.getPOV()
            left_wing_up = op_pov < 20 or 340 < op_pov
            left_wing_down = 160 < op_pov < 200
        else:
            left_wing_up = False
            left_wing_down = False

        right_wing_up = self.operator.getYButton()
        right_wing_down = self.operator.getAButton()

        if left_wing_up and self.left_activated:
            self.wings.raise_left()
        if left_wing_down and self.left_activated:
            self.wings.lower_left()
        if right_wing_up and self.right_activated:
            self.wings.raise_right()
        if right_wing_down and self.right_activated:
            self.wings.lower_right()

        INTAKE_DEADZONE = 0.2
        # Inverted due to yaxis inversion built into the joystick
        left_stick = -deadzone(self.operator.getY(LEFT), INTAKE_DEADZONE)
        right_stick = -deadzone(self.operator.getY(RIGHT), INTAKE_DEADZONE)
        self.grabber.set_left(left_stick * 0.5)
        self.grabber.set_right(right_stick * 0.5)
        # if right_trigger > TRIGGER_LEVEL and left_trigger > TRIGGER_LEVEL:
        #     self.grabber.spit(min(right_trigger, left_trigger))
        # elif right_trigger > TRIGGER_LEVEL or left_trigger > TRIGGER_LEVEL:
        #     self.grabber.absorb(max(right_trigger, left_trigger))

        # debug_encoder(self.left1, "left1: ")
        # debug_encoder(self.right1, "right1: ")
        # debug_encoder(self.left2, "left2: ")
        # debug_encoder(self.right2, "right2: ")

    def autonomousInit(self):
        print("Autonomous Begin!")
        # The game specific message is only given once autonomous starts
        # It is not avaliable during disable mode before the game starts
        # and it is not useful in teleop mode, so we only get the message here.
        game_message = wpilib.DriverStation.getInstance().getGameSpecificMessage()
        switch_position = autonomous.get_game_specific_message(game_message)

        robot_position = autonomous.Position.CENTER # TODO: have an actual way to set this outside of the program

        # alliance_side =  wpilib.DriverStation.getInstance().getAlliance()

        routine = autonomous.get_routine(robot_position=robot_position, switch_position=switch_position)

        print("Game Message: ", game_message)
        print("Switch Position: ", switch_position)
        print("Robot Position", robot_position)
        print("Routine: ", routine)
        # self.auton = autonomous.vision_reckon(self.drivetrain, self.gyro, self.vision_socket)
        if routine == autonomous.AutonomousRoutine.SIDE_TO_SAME:
            print("SIDE TO SAME SIDE AUTON")
            self.auton = autonomous.switch_to_same_side(self.grabber, self.elevator, self.drivetrain, self.gyro, self.vision_socket, switch_position)
        elif routine == autonomous.AutonomousRoutine.CENTER:
            print("CENTER AUTON")
            self.auton = autonomous.center_straight_vision(self.grabber, self.elevator, self.drivetrain, self.gyro, self.vision_socket, switch_position)
        elif routine == autonomous.AutonomousRoutine.SIDE_TO_OPPOSITE:
            print("ZIG ZAG AUTON")
            self.auton = autonomous.zig_zag_encoder(self.grabber, self.elevator, self.drivetrain, self.gyro, self.vision_socket, switch_position)
        else:
            #Use this else for testing purposes?
            print("VISION AUTO")
            self.auton = autonomous.vision_reckon(self.drivetrain, self.gyro, self.vision_socket, 0.5, "retroreflective")

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

def deadzone(val, deadzone):
    if abs(val) < deadzone:
        return 0
    return val

def debug_encoder(talon, name):
    # print(name, " encoder pos", talon.getPinStateQuadA())
    print(name, " encoder vel", talon.getQuadratureVelocity())
    # print(name, " encoder pins", talon.getQuadPinStates())

if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
