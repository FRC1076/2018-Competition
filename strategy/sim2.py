# Make 3 robots that go at different speeds drive back and forth using a queue
# as a timer.

import queue
from enum import Enum, auto

class Team(Enum):
    RED = auto()
    BLUE = auto()

class Location(Enum):
    RED_PORTAL = -15
    RED_PILE = -13 
    RP_cubes = 10
    RED_SWITCH = -8  # has cubes
    RED_SCALE = -5
    BLUE_SCALE = 5
    BLUE_SWITCH = 8  # has cubes
    BLUE_PILE =  13 # has cubes
    BLUE_PORTAL = 15

    def __init__(self, position):
        self.position = position


class Robot:
    def __init__(self, name, team, world, speed, location):
        self.name = name
        self.team = team
        self.world = world
        self.speed = speed
        self.location = location
        self.has_cube = True
    def Robot1(drive):
        Robot.name = 'Robot#1'
        Robot1.team = BLUE
        Robot1.speed = 5
        Robot1.location = BLUE_PORTAL
        Robot1.has_cube = True
        
        

        if has_cube == False:
            Robot1.pick_up
        else:     
            Robot1.put_down
    def __lt__(self, other):
        return hash(self) < hash(other)
    def world():
        if time < 150:
            return BLUE_PILE, BLUE_SWITCH, BLUE_SCALE 
            return RED_PILE, RED_SWITCH, RED_SCALE
            if BLUE_SWITCH == True:
                BLUE_SCORE += 1
            if RED_SWITCH == True:
                RED_SCORE += 1
            if RED_SCALE > BLUE_SCALE:
                RED_SCORE += 1
            if BLUE_SCALE > RED_SCALE:
                BLUE_SCORE += 1
            time += 1    
            return RED_SCORE, BLUE_SCORE        
            yield 1
    def __repr__(self):
        return f'Robot({self.name!r}, {self.location!r})'

    def drive(self, to):
        distance = abs(self.location.position - to.position)
        yield distance / self.speed
        self.location = to
    
    def pick_up(self):
        if self.has_cube or self.world[self.location]['cubes'] <= 0:
            return
        self.world[self.location]['cubes'] -= 1
        yield 2
        self.has_cube = True
    
    def put_down(self):
        if not self.has_cube:
            return
        self.has_cube = False
        yield 2
        self.world[self.location][self.team] += 1
   
    def run(self):
        self.gen = self._run()
        return self

    def _run(self):
        yield 0
   
    def resume(self):
        return next(self.gen)

# Add a "robot" for the field that every turn checks the stuff and tracks points
# Make the robots smarter

# while True:
#     handle score
#     yield 1

class ARobot(Robot):
    def _run(self):
        yield from self.drive(Location.RED_PILE)
        yield from self.pick_up()
        yield from self.drive(Location.RED_SWITCH)
        yield from self.put_down()
        yield from self.drive(Location.RED_PILE)


class BRobot(Robot):
    def _run(self):
        yield from self.drive(Location.RED_SCALE)
        yield from self.drive(Location.BLUE_SWITCH)


class CRobot(Robot):
    def _run(self):
        yield from self.drive(Location.RED_SWITCH)
        yield from self.drive(Location.RED_PILE)
        yield from self.drive(Location.BLUE_SCALE)


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
    # @Todo: Add all the other locations
    world = {
        Location.RED_PILE: {'cubes': 10, Team.RED: 0, Team.BLUE: 0},
        Location.BLUE_PILE: {'cubes': 10, Team.RED: 0, Team.BLUE: 0},
        Location.RED_SWITCH: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
        Location.BLUE_SWITCH: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
        Location.RED_SCALE: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
        Location.BLUE_SCALE: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
    }
    robots = [
        ARobot('A', Team.RED, world, 4, Location.RED_PORTAL),
        BRobot('B', Team.BLUE, world, 4, Location.BLUE_PORTAL),
        CRobot('C', Team.RED, world, 4, Location.RED_PORTAL),
    ]
    events = queue.PriorityQueue()
    for robot in robots:
        events.put((0, robot.run()))
    schedule(events)

