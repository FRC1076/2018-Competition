import wpilib
import ctre
import wpilib.drive

class Robot(wpilib.IterativeRobot):
    def robotInit(self):
        self.l_motor = ctre.WPI_TalonSRX(3)
        self.l_motor2 = ctre.WPI_TalonSRX(4)
        self.r_motor = ctre.WPI_TalonSRX(1)
        self.r_motor2 = ctre.WPI_TalonSRX(2)
        self.left = wpilib.SpeedControllerGroup(self.l_motor, self.l_motor2)
        self.right = wpilib.SpeedControllerGroup(self.r_motor, self.r_motor2)
        self.robot_drive = wpilib.drive.DifferentialDrive(self.left, self.right)
        self.stick = wpilib.Joystick(0)
        # self.encoder = wpilib.Encoder(3, 4)
        pass

    def teleopInit(self):
        print("Teleop Init")

    def teleopPeriodic(self):
        # print("l_motor speed" + str(self.l_motor.get()))
        self.robot_drive.arcadeDrive(self.stick.getY(), self.stick.getX())
        # self.l_motor.set(self.stick.getX())
        # print(self.l_motor.getQuadraturePosition() + " quad")
        # if self.r_motor.getEncVelocity() != 0:
        #     print("ENC1: " + str(self.r_motor.getEncVelocity()))
        # if self.r_motor2.getEncVelocity() != 0:
        #     print("ENC2: " + str(self.r_motor2.getEncVelocity()))
        # if self.l_motor.getEncVelocity() != 0:
        #     print("ENC3: " + str(self.l_motor.getEncVelocity()))
        # if self.l_motor2.getEncVelocity() != 0:
        #     print("ENC4: " + str(self.l_motor2.getEncVelocity()))
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass


if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
