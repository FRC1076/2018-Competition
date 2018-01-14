from subsystems.elevator import Elevator


class GetSet:
    def __init__(self, state):
        self.state = state

    def get(self):
        return self.state

    def set(self, state):
        self.state = state

def test_elevator():
    motor = GetSet(0)
    elevator = Elevator(motor)

    elevator.go_up()
    assert motor.state == 1
    elevator.go_up(speed=0.5)
    assert motor.state == 0.5

    elevator.go_down()
    assert motor.state == -1
    elevator.go_down(speed=0.5)
    assert motor.state == -0.5
