import wpilib

class Grabber:
    """
    The grabber will absorb a cube, use a sensor to know when the cube has been fully absorbed,
    and release the cube on commmand.
    """
    def __init__(self, left, right, sensor):
        self.left_motor = left
        self.right_motor = right
        self.sensor = sensor

    def set(self, speed=1.0):
        self.left_motor.set(speed)
        self.right_motor.set(-speed)

    def set_left(self, speed=1.0):
        self.left_motor.set(speed)

    def set_right(self, speed=1.0):
        self.right_motor.set(-speed)

    def has_cube(self):
        return self.sensor.get()
