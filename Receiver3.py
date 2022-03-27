# Eric Janto s1975761
import logging
import sys

from Receiver2 import Receiver2
from utils import set_up_logging


class Receiver3(Receiver2):
    def __init__(self, server_port, new_file_name):
        super(Receiver3, self).__init__(server_port, new_file_name)
        self.received_packets = {}

    def expected_seq(self):
        seqs = list(self.received_packets.keys())
        if seqs:
            return seqs[-1] + 1
        else:
            return 0

    def is_duplicate(self, seq):
        if seq in self.received_packets.keys():
            return True
        else:
            return False

    def is_in_order(self, seq):
        return seq == self.expected_seq()

    def receive_file(self):
        while True:
            message, client_address = self.receive_message()

            seq = Receiver3.get_seq(message)
            eof = Receiver3.get_eof(message)

            # If not duplicate, otherwise discard package and
            # don't send ACK.
            if not self.is_duplicate(seq):
                if self.is_in_order(seq):
                    payload = Receiver3.remove_header(message)
                    self.received_packets[seq] = payload
                    logging.debug(f'>> Packet {seq} accepted.')
                else:
                    logging.debug(f'!! Packet {seq} not accepted, expected:'
                                  f'{self.expected_seq()}')
            else:
                logging.debug(f'!! Packet {seq} discarded, duplicate detected.')

            # Send ACK for last received packet
            if self.received_packets.keys():
                last_seq = list(self.received_packets.keys())[-1]
                self.send_ACK(last_seq, client_address)

            if eof == 1:
                self.send_safety_ACKs(seq, client_address)
                break

        self.server_socket.close()
        self.write_packets_to_file(self.received_packets)


if __name__ == '__main__':
    set_up_logging('receiver3.log')

    SERVER_PORT = int(sys.argv[1])
    NEW_FILE_NAME = sys.argv[2]

    receiver = Receiver3(SERVER_PORT, NEW_FILE_NAME)
    receiver.receive_file()
