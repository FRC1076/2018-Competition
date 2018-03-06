import network

def test_read_packet():
    vision_socket = network.VisionSocket()
    vision_socket._read_packet(b'{"sender": "vision", "angle": 420, "id": 69}')
    assert vision_socket.get_angle(max_staleness=9999) == 420
    assert vision_socket.get_id() == 69
    vision_socket.close()
