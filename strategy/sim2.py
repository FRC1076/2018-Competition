# Make 3 robots that go at different speeds drive back and forth using a queue
# as a timer.

import queue


class Robot:
    def __init__(self, name):
        self.name = name

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __repr__(self):
        return f'Robot({self.name!r}, {self.delay})'
   
    def run(self):
        self.gen = self.drive()
        return self

    def drive(self):
        yield 0
   
    def resume(self):
        return next(self.gen)



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
    robots = [
        Robot('A'),
        Robot('B'),
        Robot('C'),
    ]
    events = queue.PriorityQueue()
    for robot in robots:
        events.put((0, robot.run()))
    schedule(events)
