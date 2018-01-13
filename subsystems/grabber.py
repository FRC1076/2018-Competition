import wpilib

class Grabber:
	"""
		The grabber will absorb a cube, 
		use a sensor to know when the cube has been fully absorbed,
		and release the cube on commmand.
	"""
	def __init__(self, left, right, sensor):
		self.left_motor = left
		self.right_motor = right
		self.sensor = sensor

	def absorb(self, speed=1.0):
		pass

	def spit(self, speed=1.0):
		pass

	def has_cube(self):
		pass
		