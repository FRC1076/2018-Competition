from wpilib import DoubleSolenoid
import pytest

from helper import GetSet
from subsystems.wings import Wings

Value = DoubleSolenoid.Value

@pytest.mark.skip(reason="totally different api after refactor")
def test_make_wings():
    valve_left = GetSet(Value.kOff)
    valve_right = GetSet(Value.kOff)
    center_valve_left = GetSet(Value.kOff)
    center_valve_right = GetSet(Value.kOff)

    wings = Wings(valve_left, valve_right, center_valve_left, center_valve_right,)
    wings.lower_left()
    assert valve_left.state == Value.kForward
    assert center_valve_left.state == Value.kForward

    wings.lower_right()
    assert valve_right.state == Value.kForward
    assert center_valve_right.state == Value.kForward


    wings.raise_left()
    assert valve_left.state == Value.kReverse
    assert center_valve_left.state == Value.kReverse

    wings.raise_right()
    assert valve_right.state == Value.kReverse
    assert center_valve_right.state == Value.kReverse
