from wpilib import DoubleSolenoid

from helper import GetSet
from subsystems.wings import Wings

Value = DoubleSolenoid.Value

def test_make_wings():
    valve_left = GetSet(Value.kOff)
    valve_right = GetSet(Value.kOff)

    wings = Wings(valve_left, valve_right)
    wings.lower_left()
    wings.lower_right()
    assert valve_left.state == Value.kForward
    assert valve_right.state == Value.kForward
    wings.raise_left()
    wings.raise_right()
    assert valve_left.state == Value.kReverse
    assert valve_right.state == Value.kReverse
