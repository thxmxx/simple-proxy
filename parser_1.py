import struct
import time

SERVER_QUEUE = []
CLIENT_QUEUE = []


def h_position(data, origin):
    print(f'h_position {data.hex()}')


def h_noop(data, origin):
    return data


handlers = {
    0x17030301ef00000000000000: h_position
}


def parse(data, port, origin):
    if origin == 'server':
        print(f'server[{port}] <- {data.hex()}')
    else:
        print(f'client[{port}] -> {data.hex()}')
        # CLIENT_QUEUE.append(bytearray.fromhex(
        #     '170303004a000000000000004b552272c01becea3437d1cb084cd453957a529c4a52950079ab6ccde394fc1dec38932798eaa71a735d7eb1a62dacb9f186a2fae638303e4a7425b2c003856328729e'))
    return
    while len(data) >= 2:
        packet_id = data[0:24]
        print(f'ID: {packet_id.hex()}')
        if packet_id not in handlers:
            data = data[1:]
        else:
            data = handlers.get(packet_id, h_noop)(data[24:], origin)
