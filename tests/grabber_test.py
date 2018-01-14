from subsystems.grabber import Grabber

class GetSet:
    def __init__(self, state):
        self.state = state

    def get(self):
        return self.state

    def set(self, state):
        self.state = state

def test_make_grabber():
    left_motor = GetSet(0)
    right_motor = GetSet(0)
    sensor = GetSet(False)

    grabber = Grabber(left_motor, right_motor, sensor)
    grabber.absorb()
    assert left_motor.state == 1
    assert right_motor.state == -1
    grabber.absorb(speed=0.5)
    assert left_motor.state == 0.5
    assert right_motor.state == -0.5
    grabber.spit()
    assert left_motor.state == -1
    assert right_motor.state == 1
    grabber.spit(speed=0.5)
    assert left_motor.state == -0.5
    assert right_motor.state == 0.5
    assert not grabber.has_cube()
    sensor.state = True
    assert grabber.has_cube()

   

