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

ELEVATOR1_ID = 5
ELEVATOR2_ID = 6
LEFT_GRABBER_ID = 4
RIGHT_GRABBER_ID = 3

LEFT1_ID = 1
LEFT2_ID = 2
RIGHT1_ID = 7
RIGHT2_ID = 8


# Wing Solenoid IDs
LEFT_RETRACT = 0
LEFT_CENTER_EXTEND = 2
LEFT_OUTER_EXTEND = 1
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

        # self.gyro = wpilib.ADXRS450_Gyro()
        self.gyro = navx.ahrs.AHRS.create_spi()


        self.drivetrain = Drivetrain(left, right, wpilib.DoubleSolenoid(3, 4), self.gyro, encoder_motor=self.left1)

        self.grabber = Grabber(
            ctre.WPI_TalonSRX(LEFT_GRABBER_ID),
            ctre.WPI_TalonSRX(RIGHT_GRABBER_ID),
            None,
        )
        elevator1 = ctre.WPI_TalonSRX(ELEVATOR1_ID)
        elevator2 = ctre.WPI_TalonSRX(ELEVATOR2_ID)
        elevator2.setInverted(True)
        self.elevator = Elevator(wpilib.SpeedControllerGroup(elevator1, elevator2))

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
        self.chooser.addDefault('unknown (defaults to auton line crossing)', autonomous.Position.UNKNOWN)
        self.chooser.addObject('left', autonomous.Position.LEFT)
        self.chooser.addObject('right', autonomous.Position.RIGHT)
        SmartDashboard.putData(SIDE_SELECTOR, self.chooser)

    def robotPeriodic(self):
        self.drivetrain.updatePID()
        # print("left1", self.left1.getQuadraturePosition(), "current")
        # print("left2", self.left2.getQuadraturePosition())
        # print("right1", self.right1.getQuadraturePosition())
        # print("right2", self.right2.getQuadraturePosition())
        if self.timer % 1000 == 0:
            # print(self.vision_socket.debug())
            # print('angle ', self.gyro.getAngle())
            # print('pitch ', self.gyro.getPitch())
            # print('yaw ', self.gyro.getYaw())
            # print('roll ', self.gyro.getRoll())
            # print("is bound: ", self.vision_socket.is_bound())
            print("choosen: ", self.chooser.getSelected())
            game_message = wpilib.DriverStation.getInstance().getGameSpecificMessage()
            print("game msg: ", autonomous.get_game_specific_message(game_message))
            print("routine: ", autonomous.get_routine(self.chooser.getSelected(), *autonomous.get_game_specific_message(game_message)))
        self.timer += 1

    def teleopInit(self):
        self.left_activated = False
        self.right_activated = False
        print("Teleop Init Begin!")
        self.forward = 0

    def teleopPeriodic(self):
        # Arcade Driver Controlls
        DEADZONE = 0.2
        MAX_ACCELERATION = 0.3
        goal_forward = -self.driver.getY(RIGHT)
        rotate = self.driver.getX(LEFT)

        MAX_FORWARD = 1.0
        MAX_ROTATE = 1.0

        goal_forward = deadzone(goal_forward * MAX_FORWARD, DEADZONE)
        rotate = deadzone(rotate * MAX_ROTATE, DEADZONE)

        delta = goal_forward - self.forward

        if abs(delta) < MAX_ACCELERATION:
            self.forward += delta
        else:
            self.forward += MAX_ACCELERATION * sign(delta)

        # Brake Button
        if self.driver.getXButton():
            self.drivetrain.stop()
        else:
            self.drivetrain.arcade_drive(self.forward, rotate)

        # Gear shifter, held = high gear
        gear_high = self.driver.getBumper(RIGHT)

        if gear_high:
            self.drivetrain.shift_high()
        else:
            self.drivetrain.shift_low()

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
        activate_right = self.operator.getBackButton() and self.driver.getBackButton()
        activate_left = self.operator.getStartButton() and self.driver.getStartButton()

        activate_right_released = self.operator.getBackButtonReleased() or self.driver.getBackButtonReleased()
        activate_left_released = self.operator.getStartButtonReleased() or self.driver.getStartButtonReleased()

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
            right_wing_up = op_pov < 20 or 340 < op_pov
            right_wing_down = 160 < op_pov < 200
        else:
            right_wing_up = False
            right_wing_down = False

        left_wing_up = self.operator.getYButton()
        left_wing_down = self.operator.getAButton()

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
        self.drivetrain.shift_low()
        print("Autonomous Begin!")
        # The game specific message is only given once autonomous starts
        # It is not avaliable during disable mode before the game starts
        # and it is not useful in teleop mode, so we only get the message here.
        game_message = wpilib.DriverStation.getInstance().getGameSpecificMessage()
        (switch_position, scale_position) = autonomous.get_game_specific_message(game_message)

        robot_position = self.chooser.getSelected()
        # robot_position = autonomous.Position.CENTER # TODO: have an actual way to set this outside of the program

        # alliance_side =  wpilib.DriverStation.getInstance().getAlliance()

        routine = autonomous.get_routine(robot_position=robot_position, switch_position=switch_position, scale_position=scale_position)

        print("Game Message: ", game_message)
        print("Switch Position: ", switch_position)
        print("Robot Position", robot_position)
        print("Routine: ", routine)
        # self.auton = autonomous.scale_to_same_side(self.grabber, self.elevator, self.drivetrain, self.gyro, self.vision_socket, switch_position)
      
        if routine == autonomous.AutonomousRoutine.SWITCH:
            print("SWITCH")
            self.auton = autonomous.switch_to_same_side(self.grabber, self.elevator, self.drivetrain, self.gyro, self.vision_socket, switch_position)
        elif routine == autonomous.AutonomousRoutine.SCALE:
            print("SCALE")
            self.auton = autonomous.scale_to_same_side(self.grabber, self.elevator, self.drivetrain, self.gyro, self.vision_socket, scale_position)
        elif routine == autonomous.AutonomousRoutine.ZIG_ZAG:
            print("ZIG ZAG AUTON")
            self.auton = autonomous.zig_zag(self.grabber, self.elevator, self.drivetrain, self.gyro, self.vision_socket, switch_position)
        else:
            print("AUTON LINE")
            self.auton = autonomous.dead_reckon(self.drivetrain, self.gyro)

    def autonomousPeriodic(self):
        try:
            next(self.auton)
            print("Angle", self.gyro.getAngle())
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

def sign(number):
    if number > 0:
        return 1
    else:
        return -1


def debug_encoder(talon, name):
    # print(name, " encoder pos", talon.getPinStateQuadA())
    print(name, " encoder vel", talon.getQuadratureVelocity())
    # print(name, " encoder pins", talon.getQuadPinStates())

if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
