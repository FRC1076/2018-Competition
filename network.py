import socket
import json

from autonomous import RotateAutonomous

UDP_IP = '10.10.76.2'
UDP_PORT = 5880
BUFFER_SIZE = 1024
lookFor = "cube" # Cube or retroreflective based on what you want to find

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.settimeout(0.1) # Timeout after 0.1 seconds

"""
Attempts to bind to the socket. Should be run once but may be run multiple times
if binding fails(?)
"""
def init():
    try:
        socket.bind((UDP_IP, UDP_PORT))
    except Exception as e:
        print("Could not bind: {}".format(e))

"""
Attempts to get a packet from the socket and
returns the dictionary recieved from the socket.
Throws IOError if unable to recieve the packet.
"""
def get_packet():
    data = socket.recv(BUFFER_SIZE)
    return json.loads(data.decode())

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
