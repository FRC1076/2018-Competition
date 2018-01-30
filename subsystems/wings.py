from wpilib import DoubleSolenoid

class Wings:
    """
    The wings job is to raise the other two robots on the team at least 12' off
    the ground via foldable wings that the robots will climb on. There will be 2
    valves that release pressure to pistons on each wings, which will deploy
    them.

    The wings are held by a velcro "latch" that is broken when the piston is
    released. When the velcro is broken the wings are "unlocked" and can now be
    lowered and raised.
    """
    def __init__(self, valve_left, valve_right):
        self.valve_left = valve_left
        self.valve_right = valve_right

    def lower_left(self):
        self.valve_left.set(DoubleSolenoid.Value.kForward)

    def lower_right(self):
        self.valve_right.set(DoubleSolenoid.Value.kForward)

    def raise_left(self):
        self.valve_left.set(DoubleSolenoid.Value.kReverse)

    def raise_right(self):
        self.valve_right.set(DoubleSolenoid.Value.kReverse)
