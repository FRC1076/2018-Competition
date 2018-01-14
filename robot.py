import wpilib


class Robot(wpilib.IterativeRobot):
    def robotInit(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass


if __name__ == '__main__':
    wpilib.run(Robot, physics_enabled=True)
