# Eric Janto s1975761
import time

from constants import BUFFER_SIZE, HEADER_SIZE, SEQ_SIZE
# from conversions import seq_byte_to_int

# import logging
from socket import *
import sys

# from utils import set_up_logging


class Receiver:
    def __init__(self, server_port, new_file_name):
        self.server_port = server_port
        self.new_file_name = new_file_name
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))

    @staticmethod
    def bytearray_to_int(ba, number_of_fields):
        # number_of_fields specified index - 1 until which we add
        return int.from_bytes(ba[0:number_of_fields], 'big')

    @staticmethod
    def get_header(packet):
        return packet[0:HEADER_SIZE]

    @staticmethod
    def get_seq(packet):
        header = Receiver.get_header(packet)
        return Receiver.bytearray_to_int(header, 2)

    @staticmethod
    def get_eof(packet):
        header = Receiver.get_header(packet)
        return header[HEADER_SIZE - 1]

    @staticmethod
    def remove_header(packet):
        return packet[HEADER_SIZE:]

    def receive_message(self):
        message, address = self.server_socket.recvfrom(BUFFER_SIZE)
        return message, address

    def receive_file(self):
        received_messages = []
        while True:
            message, _ = Receiver.receive_message(self)
            received_messages.append(message)
            eof = Receiver.get_eof(message)

            # logging.debug(f'Receiving packet {seq_byte_to_int(header[0:SEQ_SIZE])}.')
            # logging.debug(f'  EOF: {eof}')
            if eof == 1:
                break
        self.server_socket.close()

        with open(self.new_file_name, 'wb') as transferred_file:
            for m in received_messages:
                packet = Receiver.remove_header(m)
                transferred_file.write(packet)


if __name__ == '__main__':
    SERVER_PORT = int(sys.argv[1])
    NEW_FILE_NAME = sys.argv[2]

    # set_up_logging('receiver1.log')

    receiver = Receiver(SERVER_PORT, NEW_FILE_NAME)
    receiver.receive_file()
