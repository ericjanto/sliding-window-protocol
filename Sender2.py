# Eric Janto s1975761
from socket import *
import sys

from Sender1 import Sender
from CustomTimer import *
from constants import ACK_BUFFER_SIZE


class Sender2(Sender):
    # An additional constructor since the timeout class field is new
    def __init__(self, server_ip, server_port, file_name, timeout_ms):
        super(Sender2, self).__init__(server_ip, server_port, file_name)

        # Timeout needs to be provided in s in settimeout()
        self.timeout = timeout_ms / 1000
        self.client_socket.settimeout(self.timeout)

        self.timer = CustomTimer()

    @staticmethod
    def int_to_bytearray(x, store_in_n_bytes):
        return bytearray(x.to_bytes(store_in_n_bytes, byteorder='big'))

    @staticmethod
    def bytearray_to_int(ba, number_of_fields):
        return int.from_bytes(ba[0:number_of_fields], 'big')

    # Checks whether a package transfer is ACKnowledged
    @staticmethod
    def is_ACK(current_seq, received_ack_packet):
        rap_int = Sender2.bytearray_to_int(received_ack_packet, 2)
        return current_seq == rap_int

    @staticmethod
    def calculate_throughput(total_time_in_s, datasize_in_bytes):
        # Factor of (1000) since we want to output in kilobytes/s
        return (datasize_in_bytes / 1000) / total_time_in_s

    def get_file_size(self):
        return len(Sender.read_file(self.file_name))

    def send_file_content(self):
        file_content = Sender.read_file(self.file_name)
        packets = Sender.add_headers(Sender.get_payloads(file_content))

        retransmissions = 0
        transmission_time = 0

        self.timer.start_timer()
        for s in packets:
            success = False
            resent = 0
            while not success:
                # logging.debug(f'Sending packet {s}. Attempt: {resent}.')
                self.client_socket.sendto(packets[s], (self.server_ip, self.server_port))

                try:
                    message, _ = self.client_socket.recvfrom(ACK_BUFFER_SIZE)
                    if Sender2.is_ACK(s, message):
                        success = True
                        # If last ACK:
                        if s == len(packets) - 1:
                            transmission_time = self.timer.get_current_timer_value()
                except error:
                    # logging.debug(f'Resending packet {s} because ACK not received within time window.')
                    resent += 1

            retransmissions += resent
        self.print_results(retransmissions, transmission_time)

    def print_results(self, retransmissions, transmission_time):
        throughput = round(Sender2.calculate_throughput(transmission_time, self.get_file_size()), 2)
        print(f'{retransmissions} {throughput}')


if __name__ == '__main__':
    # server_ip is either host name (resolved by OS DNS) or IP address
    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    # Positive integer in ms
    TIMEOUT_MS = int(sys.argv[4])

    sender = Sender2(SERVER_IP, SERVER_PORT, FILE_NAME, TIMEOUT_MS)
    sender.send_file_content()
