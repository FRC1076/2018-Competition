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

    def __init__(self, left_retract, right_retract,
                left_out_extend, right_out_extend,
                left_center_extend, right_center_extend,
            ):
        self.left_out = SolenoidPair(left_retract, left_out_extend)
        self.right_out = SolenoidPair(right_retract, right_out_extend)
        self.left_center = SolenoidPair(left_retract, left_center_extend)
        self.right_center = SolenoidPair(right_retract, right_center_extend)

    def lower_left(self):
        self.left_out.retract()
        self.left_center.retract()

    def lower_right(self):
        self.right_out.retract()
        self.right_center.retract()

    def raise_left(self):
        self.left_out.extend()
        self.left_center.extend()

    def raise_right(self):
        self.right_out.extend()
        self.right_center.extend()

    def raise_center_left(self):
        self.left_center.extend()

    def raise_center_right(self):
        self.right_center.extend()


class SolenoidPair:
    def __init__(self, retract, extend):
        self._retract = retract
        self._extend = extend

    def retract(self):
        self._retract.set(True)
        self._extend.set(False)

    def extend(self):
        self._extend.set(True)
        self._retract.set(False)
