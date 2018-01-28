# Make 3 robots that go at different speeds drive back and forth using a queue
# as a timer.

import queue
import enum

class Team(enum.Enum):
    RED = 0
    BLUE = 1

class Robot:
    def __init__(self, name, team, world):
        self.name = name
        self.team = team
        self.world = world

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __repr__(self):
        return f'Robot({self.name!r})'
   
    def run(self):
        self.gen = self.drive()
        return self

    def drive(self):
        yield 0
   
    def resume(self):
        return next(self.gen)


class ARobot(Robot):
    def drive(self):
        yield 5
        yield 3
        yield 1


class BRobot(Robot):
    def drive(self):
        yield 6
        yield 4
        yield 2


class CRobot(Robot):
    def drive(self):
        yield 7
        yield 6
        yield 5


def schedule(events):
    while not events.empty():
        time, robot = events.get()
        print(time, robot)
        if time > 150:
            break
        try:
            delay = robot.resume()
            events.put((time + delay, robot))
        except StopIteration:
            pass


if __name__ == '__main__':
    world = {}
    robots = [
        ARobot('A', Team.RED, world),
        BRobot('B', Team.BLUE, world),
        CRobot('C', Team.RED, world),
    ]
    events = queue.PriorityQueue()
    for robot in robots:
        events.put((0, robot.run()))
    schedule(events)
