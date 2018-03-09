from helper import GetSet
from subsystems.grabber import Grabber


def test_make_grabber():
    left_motor = GetSet(0)
    right_motor = GetSet(0)
    sensor = GetSet(False)

    grabber = Grabber(left_motor, right_motor, sensor)
    grabber.set()
    assert left_motor.state == -1
    assert right_motor.state == -1
    grabber.set(speed=0.5)
    assert left_motor.state == -0.5
    assert right_motor.state == -0.5
    grabber.set(speed=-1.0)
    assert left_motor.state == 1
    assert right_motor.state == 1
    grabber.set(speed=-0.5)
    assert left_motor.state == 0.5
    assert right_motor.state == 0.5
    assert not grabber.has_cube()
    sensor.state = True
    assert grabber.has_cube()
