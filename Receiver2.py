# Eric Janto s1975761
import sys

from Receiver1 import Receiver
from constants import BUFFER_SIZE, HEADER_SIZE, ACK_SIZE


class Receiver2(Receiver):
    # Checks whether a received packet is a retransmission
    # Do this by checking whether its SEQ is different to the
    # most recently received packet SEQ, or the same
    def is_duplicate(self, received_packet):
        # Maybe need to handle duplicate packets at some point,
        # but atm duplicates just replace packets in the dictionary
        # so duplicates are never written to a file multiple times
        pass

    @staticmethod
    def int_to_bytearray(x, store_in_n_bytes):
        return bytearray(x.to_bytes(store_in_n_bytes, byteorder='big'))

    def send_ACK(self, seq, client_address):
        # Create ACK (2 bytes = 16-bit seq number)
        # This can just be the seq of the received packet
        ack = Receiver2.int_to_bytearray(seq, ACK_SIZE)
        self.server_socket.sendto(ack, client_address)

    def write_packets_to_file(self, packets):
        with open(self.new_file_name, 'wb') as transferred_file:
            for s in packets:
                transferred_file.write(packets[s])

    def receive_file(self):
        # Receive packets
        packets = {}
        while True:
            # client_address is client IP and port
            message, client_address = self.receive_message()

            seq = Receiver2.get_seq(message)
            eof = Receiver2.get_eof(message)

            packet = Receiver2.remove_header(message)
            packets[seq] = packet
            self.send_ACK(seq, client_address)

            if eof == 1:
                self.send_safety_ACKs(seq, client_address)
                break

        self.server_socket.close()
        self.write_packets_to_file(packets)

    # The last ACK package might get lost in which case the
    # sender does not terminate. This is a simple-crude safety-
    # measure to prevent this.
    def send_safety_ACKs(self, seq, client_address):
        safety_threshold = 3
        for i in range(safety_threshold):
            self.send_ACK(seq, client_address)


if __name__ == '__main__':
    SERVER_PORT = int(sys.argv[1])
    NEW_FILE_NAME = sys.argv[2]

    # set_up_logging('receiver2.log')

    receiver = Receiver2(SERVER_PORT, NEW_FILE_NAME)
    receiver.receive_file()
