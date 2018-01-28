# Make 3 robots that go at different speeds drive back and forth using a queue
# as a timer.

import queue


class Robot:
    def __init__(self, name, delay):
        self.name = name
        self.delay = delay

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __repr__(self):
        return f'Robot({self.name!r}, {self.delay})'


robots = {
    'A': Robot('A', 3),
    'B': Robot('B', 7),
    'C': Robot('C', 2),
}

events = queue.PriorityQueue()
for robot in robots.values():
    events.put((0, robot))

for i in range(30):
    if events.empty():
        break

    time, robot = events.get()
    print(i, time, robot)
    events.put((robot.delay + time, robot))
    
