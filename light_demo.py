import network
import time

socket = network.LIGHT_RING_SOCKET


for i in range(0, 10):
    network.send_light_message(socket, i % 4)
    print(i)
    time.sleep(5)


