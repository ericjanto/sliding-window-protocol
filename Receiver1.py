# Eric Janto s1975761
import time

from constants import BUFFER_SIZE, HEADER_SIZE, SEQ_SIZE
from conversions import seq_byte_to_int

# import logging
from socket import *
import sys

from utils import set_up_logging


class Receiver:
    def __init__(self, server_port, new_file_name):
        self.server_port = server_port
        self.new_file_name = new_file_name
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))

    def receive_message(self):
        message, address = self.server_socket.recvfrom(BUFFER_SIZE)
        return message, address

    def receive_file(self):
        received_messages = []
        while True:
            message, _ = Receiver.receive_message(self)
            received_messages.append(message)
            header = message[0:HEADER_SIZE]
            eof = header[HEADER_SIZE - 1]

            # logging.debug(f'Receiving packet {seq_byte_to_int(header[0:SEQ_SIZE])}.')
            # logging.debug(f'  EOF: {eof}')
            if eof == 1:
                break
        self.server_socket.close()

        with open(self.new_file_name, 'wb') as transferred_file:
            for m in received_messages:
                packet = m[HEADER_SIZE:]
                transferred_file.write(packet)
                time.sleep(0.1)


if __name__ == '__main__':
    SERVER_PORT = int(sys.argv[1])
    NEW_FILE_NAME = sys.argv[2]

    # set_up_logging('receiver1.log')

    receiver = Receiver(SERVER_PORT, NEW_FILE_NAME)
    receiver.receive_file()
