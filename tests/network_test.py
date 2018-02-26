import network

def test_read_packet():
    vision_socket = network.VisionSocket()
    vision_socket._read_packet(b'{"sender": "vision", "angle": 420, "id": 69}')
    assert vision_socket.get_angle(max_staleness=9999) == 420
    assert vision_socket.get_id() == 69
    vision_socket.close()


def test_light_message():
    socket = MockSocket()
    network.send_light_message(socket, 5)


def test_get_socket():
    socket = network._get_socket('0.0.0.0', 0)
    socket.close()

class MockSocket:
    def __init__(self):
        pass

    def sendto(self, thing, address):
        pass
