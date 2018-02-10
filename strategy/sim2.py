# Make 3 robots that go at different speeds drive back and forth using a queue
# as a timer.

import queue
from enum import Enum, auto

class Team(Enum):
    RED = auto()
    BLUE = auto()

    def opposing(self):
        if self == Team.RED:
            return Team.BLUE
        else:
            return Team.RED

class Location(Enum):
    RED_PORTAL = -15
    RED_PILE = -13 
    RED_SWITCH = -8  # has cubes
    RED_SCALE = -5
    BLUE_SCALE = 5
    BLUE_SWITCH = 8  # has cubes
    BLUE_PILE =  13 # has cubes
    BLUE_PORTAL = 15

    def __init__(self, position):
        self.position = position

    @staticmethod
    def pile(team):
        if team == Team.RED:
            return Location.RED_PILE
        else:
            return Location.BLUE_PILE


class Robot:
    def __init__(self, name, team, world, speed, location):
        self.name = name
        self.team = team
        self.world = world
        self.speed = speed
        self.location = location
        self.has_cube = True
    
    def __lt__(self, other):
        return hash(self) < hash(other)

    def __repr__(self):
        return f'Robot({self.name!r}, {self.location!r})'

    def scale(self, team):
        return (self.world[Location.RED_SCALE][team] +
                self.world[Location.BLUE_SCALE][team])

    def red_switch(self, team):
        return self.world[Location.RED_SWITCH][team]

    def blue_switch(self, team):
        return self.world[Location.BLUE_SWITCH][team]

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

class Score(Robot):
    def _run(self):
        while True:
            if self.scale(Team.RED) > self.scale(Team.BLUE):
                self.world['score'][Team.RED] += 1
            if self.scale(Team.BLUE) > self.scale(Team.RED):
                self.world['score'][Team.BLUE] += 1

            if self.red_switch(Team.RED) > self.red_switch(Team.BLUE):
                self.world['score'][Team.RED] += 1
            
            if self.blue_switch(Team.BLUE) > self.blue_switch(Team.RED):
                self.world['score'][Team.BLUE] += 1

            yield 1

    def __repr__(self):
        red = self.world['score'][Team.RED]
        blue = self.world['score'][Team.BLUE]
        return f'''
====================
           Red  Blue
   Score {red:>5} {blue:>5}
Switch R {self.red_switch(Team.RED):>5} {self.red_switch(Team.BLUE):>5}
   Scale {self.scale(Team.RED):>5} {self.scale(Team.BLUE):>5}
Switch B {self.blue_switch(Team.RED):>5} {self.blue_switch(Team.BLUE):>5}
===================='''


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


class ContestBot(Robot):
    def pick_contested_spot(self):
        if self.scale(self.team) <= self.scale(self.team.opposing()):
            pass
        # @Todo: Pick a location to go to
        self.contested_spot = None

    def _run(self):
        while True:
            yield from self.pick_contested_spot()
            # @Todo: Pick cubes from locations more smartly
            yield from self.drive(Location.pile(self.team))
            yield from self.pick_up()
            yield from self.drive(self.contested_spot)
            yield from self.put_down()


def schedule(events):
    while not events.empty():
        time, robot = events.get()
        if time > 150:
            break
        print(time, robot)
        try:
            delay = robot.resume()
            events.put((time + delay, robot))
        except StopIteration:
            pass


if __name__ == '__main__':
    # @Todo: Add all the other locations
    world = {
        'score': {Team.RED: 0, Team.BLUE: 0},
        Location.RED_PILE: {'cubes': 10},
        Location.BLUE_PILE: {'cubes': 10},
        Location.RED_SWITCH: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
        Location.BLUE_SWITCH: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
        Location.RED_SCALE: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
        Location.BLUE_SCALE: {'cubes': 0, Team.RED: 0, Team.BLUE: 0},
    }
    robots = [
        Score('Score', None, world, 0, None),
        ContestBot('R1', Team.RED, world, 4, Location.RED_PORTAL),
        ContestBot('R2', Team.RED, world, 4, Location.RED_PORTAL),
        ContestBot('R3', Team.RED, world, 4, Location.RED_PORTAL),
        ContestBot('B1', Team.BLUE, world, 4, Location.BLUE_PORTAL),
        ContestBot('B2', Team.BLUE, world, 4, Location.BLUE_PORTAL),
        ContestBot('B3', Team.BLUE, world, 4, Location.BLUE_PORTAL),
    ]
    events = queue.PriorityQueue()
    for robot in robots:
        events.put((0, robot.run()))
    schedule(events)

