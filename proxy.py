import socket
from threading import Thread
import parser_1 as parser
import importlib


class Proxy2Server(Thread):

    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.game = None
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.host, self.port))

    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                try:
                    parser.parse(data, self.port, 'server')
                    if len(parser.CLIENT_QUEUE) > 0:
                        pkt = parser.CLIENT_QUEUE.pop()
                        # print "got queue client: {}".format(pkt.encode('hex'))
                        self.game.sendall(pkt)
                except Exception as e:
                    print(f'server[{self.port}] {e}')
                # forward to client
                self.game.sendall(data)


class Game2Proxy(Thread):

    def __init__(self, host, port):
        super(Game2Proxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(1)
        self.game, addr = sock.accept()

    def run(self):
        while True:
            data = self.game.recv(4096)
            if data:
                try:
                    parser.parse(data, self.port, 'client')
                    if len(parser.CLIENT_QUEUE) > 0:
                        pkt = parser.CLIENT_QUEUE.pop()
                        # print "got queue client: {}".format(pkt.encode('hex'))
                        self.game.sendall(pkt)
                except Exception as e:
                    print(f'server[{self.port}] {e}')
                # forward to server
                self.server.sendall(data)


class Proxy(Thread):
    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        print(f"Proxy({self.port}) setting up")
        self.g2p = Game2Proxy(self.from_host, self.port)
        self.p2s = Proxy2Server(self.to_host, self.port)
        print(f"Proxy({self.port}) connection stabilished")
        self.g2p.server = self.p2s.server
        self.p2s.game = self.g2p.game

        self.g2p.start()
        self.p2s.start()


master_server = Proxy('0.0.0.0', '45.66.96.52', 443)
master_server.start()

while True:
    try:
        importlib.reload(parser)
    except Exception as e:
        print(f'{e}')
