import network

def test_read_packet():
    vision_socket = network.VisionSocket()
    vision_socket._read_packet(b'{"sender": "vision", "object": "cube", "angle": 420, "id":  69}')
    assert vision_socket.get_angle(key="cube", max_staleness=9999) == 420
    assert vision_socket.get_id() == 69

    vision_socket._read_packet(b'{"sender": "vision", "object": "retroreflective", "angle": 1337, "id":  1234}')
    assert vision_socket.get_angle(key="retroreflective", max_staleness=9999) == 1337
    vision_socket.close()


def test_no_key():
    vision_socket = network.VisionSocket()
    assert vision_socket.get_angle(key="cube", max_staleness=9999) == None
    vision_socket.close()
