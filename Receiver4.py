# Eric Janto s1975761
# import logging
import sys
from socket import *

from Receiver3 import Receiver3
from constants import TERMINATION_TIMEOUT
# from utils import set_up_logging, current_window_to_string


class Receiver4(Receiver3):
    def __init__(self, server_port, new_file_name, window_size):
        super(Receiver4, self).__init__(server_port, new_file_name)
        self.window_size = window_size
        self.current_window = {}
        self.base_seq = 0
        self.server_socket.settimeout(TERMINATION_TIMEOUT)

        # Writing to a file is a costly process so now changing to a
        # buffer approach since it might slow down the receiving process otherwise.
        self.file_buffer = bytearray()

    def receive_file(self):
        while True:
            message, server_address = self.receive_message()

            seq = Receiver4.get_seq(message)
            eof = Receiver4.get_eof(message)

            # logging.debug(f'Received packet {seq}.')

            if self.is_in_current_window(seq):
                # logging.debug(f'Accepted packet {seq} for window with base'
                # f'{self.base_seq}. Sending ACK.')
                self.send_ACK(seq, server_address)
                payload = self.remove_header(message)
                self.current_window[seq] = payload

                if seq == self.base_seq:
                    self.forward_window()
            elif self.is_in_previous_window(seq):
                # logging.debug(f'Packet {seq} previously received, sending ACK.'
                # f'Current window base: {self.base_seq}.')
                self.send_ACK(seq, server_address)
            if self.all_packets_received(eof):
                while True:
                    try:
                        message, server_address = self.receive_message()
                        seq = self.get_seq(message)
                        self.send_safety_ACKs(seq, server_address)
                    except timeout:
                        break
                break

        self.server_socket.close()
        self.write_buffer_to_file()

    def forward_window(self):
        # Write and remove consecutive packets from window
        # and keep shifting the window base
        current_seq = self.base_seq

        while current_seq == self.base_seq:
            self.file_buffer += self.current_window[current_seq]
            del self.current_window[self.base_seq]

            self.base_seq += 1

            if len(self.current_window.keys()) > 0:
                keys = list(self.current_window.keys())
                keys.sort()
                current_seq = keys[0]
            else:
                break

        # logging.debug(f'Forwarded window. New status:\n\n'
        # f'{current_window_to_string(self.base_seq, 0, self.window_size)}')

    def is_in_current_window(self, seq):
        return seq in range(self.base_seq, self.base_seq + self.window_size)

    # check whether its seq is in [rcv_base_seq-N, rcv_base-1]. If so, the packet
    # has been previously acknowledged but the receiver still needs to send an ACK for it.
    # This ensures that the sender’s window can move forward and does not get
    # stuck on packets where it does not know that they have been received already.
    def is_in_previous_window(self, seq):
        return seq in range(self.base_seq - self.window_size, self.base_seq)

    # eof == 1 not sufficient, second condition ensures that previous
    # packets have been received too.
    def all_packets_received(self, eof):
        return eof == 1 and self.window_is_empty()

    def window_is_empty(self):
        return len(self.current_window) == 0

    def write_buffer_to_file(self):
        with open(self.new_file_name, 'wb') as new_file:
            new_file.write(self.file_buffer)


if __name__ == '__main__':
    # set_up_logging('receiver4.log')

    SERVER_PORT = int(sys.argv[1])
    NEW_FILE_NAME = sys.argv[2]
    WINDOW_SIZE = int(sys.argv[3])

    receiver = Receiver4(SERVER_PORT, NEW_FILE_NAME, WINDOW_SIZE)
    receiver.receive_file()
