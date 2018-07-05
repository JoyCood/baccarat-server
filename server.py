import os
import daemon
import logging
import socketserver
import struct
from docs import conf
from importlib import import_module as loader

LEVEL = logging.DEBUG if 'DEBUG' in os.environ else logging.INFO
FORMAT = '[%(levelname)s]: %(asctime)-15s %(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=LEVEL, format=FORMAT, datefmt=DATEFMT)

class RequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.logger = logging.getLogger()

    def handle(self):
        while True:
            header = self.request.recv(conf.HEADER_LENGTH)
            (body_length, protocol) = struct.unpack('>2I', header)
            self.logger.info('body_length:%d protocol:%d', body_length, protocol)
            data = self.request.recv(body_length)
            module = loader('baccarat.handler')
            module.handle(self.request, protocol, data, self.logger)

    def finish(self):
        pass

class BaccaratServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def handle_error(self, request, client_address):
        print('handle_error')
        raise ValueError('unknow error')

Server = BaccaratServer((conf.HOST, conf.PORT), RequestHandler)
Server.serve_forever()

