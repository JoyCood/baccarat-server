import struct
from . import ProtocolException

def send(socket, protocol, data):
    if not isinstance(protocol, int):
        raise ProtocolError("protocol must an integer number")

    (body_length, packet) = pack(protocol, data)
    header = struct.pack('>2I', body_length, protocol)
    packet = header + packet
    socket.sendall(packet)

def pack(protocol, data):
    if not isinstance(data, bytes):
        body_length = data.ByteSize()
        packet = data.SerializeToString()
    else:
        body_length = len(data)
        packet = data
    return (body_length, packet)

