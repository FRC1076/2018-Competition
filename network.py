import json
import socket
import time
from threading import Thread

UDP_IP = '10.10.76.2' # 0.0.0.0
UDP_PORT = 5880
BUFFER_SIZE = 1024

class MockSocket(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        pass

    def update_packet(self):
        pass

    def get_angle(self, key, max_staleness):
        return 15

    def is_bound(self):
        print("WARNING: This is a mock socket!")
        return True

    def close(self):
        pass

    def get_id(self):
        return -2 # -2 is never a valid packet ID

    def debug(self):
        pass


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
        self.vision_dict = dict()
        self.running = True
        # Marks that this thread is a Daemon, meaning the thread will be killed
        # automatically when the main thread exits. This is done to prevent pytest
        # from hanging forever (since it is waiting for all threads to exit and I
        # can't seem to figure out how to make threads exit as a non-daemon thread)
        self.daemon = True
        self.packet_id = -1 # -1 is never a valid packet ID


    """
    Called as part of the Thread API. Don't call this yourself, use start()
    instead to start the thread.
    """
    def run(self):
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                self._read_packet(data)
            except IOError as e:
                pass
            except KeyError as e:
                print(e)
        print("good bye sockets")

    """
    Read a packet from the socket, and
    updating the relevant values from said packets.
    """
    def _read_packet(self, data):
        parsed = json.loads(data.decode())
        if parsed["sender"] == "vision":
            key = parsed["object"]
            self.vision_dict[key] = parsed["angle"]
            self.packet_id = parsed["id"]
        self.last_packet_time = time.time()

    def debug(self):
        print("time: ", self.last_packet_time)
        print("id: ", self.packet_id)
        print("angle (cube): ", self.get_angle(key="cube", max_staleness=1.0))
        print("angle (retro): ", self.get_angle(key="retroreflective", max_staleness=1.0))
        print("all angles: ", self.vision_dict)

    """
    Returns the most recently received angle, or none if
    the max_staleness is exceeded (in seconds)
    """
    def get_angle(self, key, max_staleness):
        if max_staleness > time.time() - self.last_packet_time:
            try:
                return self.vision_dict[key]
            except KeyError:
                return None
        else:
            # print("Stale data! {}".format(time.time() - self.last_packet_time))
            return None

    def get_id(self):
        return self.packet_id

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
        self.running = False

"""
Builds a RotateAutonomous object which attempts to rotate towards the target.
If it cannot get a packet, it will return a RotateAutonomous object which
does no rotation
"""
def rotate_to_target(drivetrain, gyro, speed):
    try:
        json = get_packet()
    except IOError as e:
        print("Failed to get a packet: {}".format(e))
        return RotateAutonomous(drivetrain, gyro, 0, 0.0)

    if json["sender"] == "vision":
        if json["object"] == lookFor:
            angle = json["angle"]
            return RotateAutonomous(drivetrain, gyro, angle, speed)
