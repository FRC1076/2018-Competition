import socket
import json

from autonomous import RotateAutonomous

UDP_IP = '10.10.76.2'
UDP_PORT = 5880
BUFFER_SIZE = 1024
lookFor = "cube" # Cube or retroreflective based on what you want to find

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def init():
    try:
        socket.bind((UDP_IP, UDP_PORT))
        socket.settimeout(1) # Timeout after 1 second
    except Exception as e:
        print("Could not bind: {}".format(e))


def debug():
    try:
        data = socket.recv(BUFFER_SIZE)
    except IOError:
        print("Timed out!")
        return
    print("got packet: " + data.decode())
    print(json.loads(data.decode()))

def rotate_to_target(drivetrain, gyro, speed):
    try:
        data = socket.recv(BUFFER_SIZE)
    except IOError:
        print("Timed out!")
        return

    json = json.loads(data)
    print(json)

    if json["sender"] == "vision":
        if json["object"] == lookFor:
            angle = json["angle"]
            rotate = autonomous.RotateAutonomous(drivetrain, gyro, angle, speed)
            rotate.init()
            yield from rotate.execute()



