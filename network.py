import json
import socket
import time
from threading import Thread

from autonomous import RotateAutonomous

UDP_IP = '10.10.76.2'
UDP_PORT = 5880
BUFFER_SIZE = 1024

class MockSocket(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        pass

    def update_packet(self):
        pass

    def get_angle(self, max_staleness):
        return 15

    def is_bound(self):
        return True

class VisionSocket(Thread):
    """
    The VisionSocket reads from a socket, processing incoming packets from
    the vision sensor.
    """
    def __init__(self):
        Thread.__init__(self)
        self.bound = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.1) # Timeout after 0.1 seconds
        try:
            self.socket.bind((UDP_IP, UDP_PORT))
            self.bound = True
        except IOError as e:
            print("Could not bind: {}".format(e))
        self.last_packet_time = time.time()
        self.angle = None
        self.closed = False

    """
    Called as part of the Thread API. Don't call this yourself, use start()
    instead to start the thread.
    """
    def run(self):
        while True:
            try:
                self._read_packet()
            except IOError as e:
                pass
            # Return from the function if the socket has been closed
            # This ends the thread
            if self.closed:
                break

    """
    Read a packet from the socket, and
    updating the relevant values from said packets.
    """
    def _read_packet(self):
        data = self.socket.recv(BUFFER_SIZE)
        parsed = json.loads(data.decode())
        if parsed["sender"] == "vision":
            self.angle = parsed["angle"]/30.0
        self.last_packet_time = time.time()

    """
    Returns the most recently received angle, or none if
    the max_staleness is exceeded (in seconds)
    """
    def get_angle(self, max_staleness):
        if max_staleness > time.time() - self.last_packet_time:
            return self.angle
        else:
            return None

    """
    Returns true if the socket is bound to the IP adress. Use for debugging.
    """
    def is_bound(self):
        return self.bound

    """
    Close the vision socket and end the thread. Should be called only once(?)
    """
    def close(self):
        self.socket.close()
        self.closed = True

"""
Builds a RotateAutonomous object which attempts to rotate towards the target.
If it cannot get a packet, it will return a RotateAutonomous object which
does no rotation
"""
def rotate_to_target(drivetrain, gyro, speed):
    try:
        json = get_packet()
    except IOError as e:
        print(f"Failed to get a packet: {e}")
        return RotateAutonomous(drivetrain, gyro, 0, 0.0)

    if json["sender"] == "vision":
        if json["object"] == lookFor:
            angle = json["angle"]
            return RotateAutonomous(drivetrain, gyro, angle, speed)
