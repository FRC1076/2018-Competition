import autonomous
import ctre
import network
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
        if self.timer % 250 == 0:
            print("angle: ", self.vision_socket.get_angle(1.0))
            print("ID: ", self.vision_socket.get_id())
            # print("is bound: ", self.vision_socket.is_bound())
            # print("choosen: ", self.chooser.getSelected())
            # game_message = wpilib.DriverStation.getInstance().getGameSpecificMessage()
            # print("game msg: ", autonomous.get_game_specific_message(game_message))
            # print("routine: ", autonomous.get_routine(self.chooser.getSelected(), autonomous.get_game_specific_message(game_message)))
        self.timer += 1

    def teleopInit(self):
        print("Teleop Init Begin!")

    def teleopPeriodic(self):
        # @Todo: Deadzone these
        DEADZONE = 0.1
        forward = -self.driver.getY(RIGHT)
        rotate = self.driver.getX(LEFT)

        MAX_FORWARD = 0.8
        MAX_ROTATE = 1.0

        forward = deadzone(forward * MAX_FORWARD, DEADZONE)
        rotate = deadzone(rotate * MAX_ROTATE, DEADZONE)

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

        INTAKE_DEADZONE = 0.2
        left_stick = deadzone(self.operator.getY(LEFT), INTAKE_DEADZONE)
        right_stick = deadzone(self.operator.getY(RIGHT), INTAKE_DEADZONE)
        self.grabber.set_left(left_stick * 0.5)
        self.grabber.set_right(right_stick * 0.5)
        # if right_trigger > TRIGGER_LEVEL and left_trigger > TRIGGER_LEVEL:
        #     self.grabber.spit(min(right_trigger, left_trigger))
        # elif right_trigger > TRIGGER_LEVEL or left_trigger > TRIGGER_LEVEL:
        #     self.grabber.absorb(max(right_trigger, left_trigger))

        debug_encoder(self.left1, "left1: ")
        debug_encoder(self.right1, "right1: ")
        debug_encoder(self.left2, "left2: ")
        debug_encoder(self.right2, "right2: ")

    def autonomousInit(self):
        print("Autonomous Begin!")
        # The game specific message is only given once autonomous starts
        # It is not avaliable during disable mode before the game starts
        # and it is not useful in teleop mode, so we only get the message here.
        game_message = wpilib.DriverStation.getInstance().getGameSpecificMessage()
        switch_position = autonomous.get_game_specific_message(game_message)
        robot_position = autonomous.Position.CENTER # TODO: have an actual way to set this outside of the program

        alliance_side =  wpilib.DriverStation.getInstance().getAlliance()

        routine = autonomous.get_routine(robot_position=robot_position, switch_position=switch_position)
        print("Switch Position: ", switch_position)
        self.auton = autonomous.test_auton(self.drivetrain, self.gyro, self.vision_socket, switch_position)
        # if routine == autonomous.AutonomousRoutine.CENTER:
        #     self.auton = autonomous.center_to_switch(self.drivetrain, self.gyro, self.vision_socket, switch_position)
        # elif routine == autonomous.AutonomousRoutine.SIDE_TO_SAME:
        #     self.auton = autonomous.switch_same_side(self.drivetrain, self.gyro, self.vision_socket, switch_position)
        # elif routine == autonomous.AutonomousRoutine.SIDE_TO_OPPOSITE:
        #     self.auton = autonomous.switch_opposite_side(self.drivetrain, self.gyro, self.vision_socket, switch_position)
        # else:
        #     # Default to the center autonomous
        #     self.auton = autonomous.center_to_switch(self.drivetrain, self.gyro, self.vision_socket, switch_position)


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
