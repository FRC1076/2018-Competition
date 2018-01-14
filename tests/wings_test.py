from subsystems.wings import Wings
from wpilib import DoubleSolenoid

Value = DoubleSolenoid.Value

class GetSet:
    def __init__(self, state):
        self.state = state

    def get(self):
        return self.state

    def set(self, state):
        self.state = state

def test_make_wings():
    valve_left = GetSet(Value.kOff)
    valve_right = GetSet(Value.kOff)
    latch_left = GetSet(0)
    latch_right = GetSet(0)

    wings = Wings(valve_left, valve_right, latch_left, latch_right)
    wings.lower_left()
    wings.lower_right()
    assert valve_left.state == Value.kForward 
    assert valve_right.state == Value.kForward
    wings.raise_left()
    wings.raise_right()
    assert valve_left.state == Value.kReverse
    assert valve_right.state == Value.kReverse
