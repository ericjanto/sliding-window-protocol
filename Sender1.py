# Eric Janto s1975761
# import logging
from socket import *
import sys
from time import sleep

from constants import PAYLOAD_SIZE, HEADER_SIZE
from conversions import seq_int_to_byte, eof_int_to_byte
# from utils import set_up_logging


# Implements a basic rdt 1.0 sender-receiver protocol
# assuming an ideally functional link layer.
class Sender:
    def __init__(self, server_ip, server_port, file_name):
        self.server_ip = server_ip
        self.server_port = server_port
        self.file_name = file_name
        self.client_socket = socket(AF_INET, SOCK_DGRAM)

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'rb') as f:
            return bytearray(f.read())

    @staticmethod
    def get_payloads(file_content):
        payloads = {}
        seq = 0
        start = 0
        stop = PAYLOAD_SIZE

        while start <= len(file_content):
            # For last package: only send file content reminder
            if stop > len(file_content):
                stop = len(file_content)

            payload = file_content[start:stop]
            payloads[seq] = payload

            if stop == len(file_content):
                break
            else:
                start = stop

            stop += PAYLOAD_SIZE
            seq += 1
        return payloads

    @staticmethod
    def int_to_bytearray(x, store_in_n_bytes):
        return bytearray(x.to_bytes(store_in_n_bytes, byteorder='big'))

    @staticmethod
    def assemble_packets(payloads_l):
        packets_l = {}

        for s in payloads_l:
            packet = bytearray(HEADER_SIZE + PAYLOAD_SIZE)
            header = bytearray(HEADER_SIZE)

            seq_in_byte = Sender.int_to_bytearray(s, 2)

            eof = 1 if s == len(payloads_l) - 1 else 0
            eof_in_byte = bytearray(eof.to_bytes(1, byteorder='big'))

            header[0] = seq_in_byte[0]
            header[1] = seq_in_byte[1]
            header[2] = eof_in_byte[0]

            packet[0] = header[0]
            packet[1] = header[1]
            packet[2] = header[2]
            packet[3:] = payloads_l[s]
            packets_l[s] = packet

        return packets_l

    # For some reason, the below refactored version of assemble_packets
    # leads to less passed test iterations.
    @staticmethod
    def add_headers(payloads):
        packets = {}
        for s in payloads:
            seq_byte = seq_int_to_byte(s)
            eof = 1 if s == len(payloads) - 1 else 0
            eof_in_byte = eof_int_to_byte(eof)

            header = seq_byte + eof_in_byte
            packet = header + payloads[s]
            packets[s] = packet

        return packets

    def send_packet(self, server_ip, server_port, packet):
        # logging.debug(f'Sending packet {seq_byte_to_int(packet[0:SEQ_SIZE])}.')
        # logging.debug(f'  EOF: {packet[HEADER_SIZE - 1]}')
        self.client_socket.sendto(packet, (server_ip, server_port))

    def send_file_content(self):
        file_content = Sender.read_file(self.file_name)
        payloads = Sender.get_payloads(file_content)
        # packets = Sender.add_headers(payloads)
        packets = Sender.assemble_packets(payloads)

        for s in packets:
            self.send_packet(self.server_ip, self.server_port, packets[s])
            # Prevent packet loss due to internal OS buffering
            sleep(0.01)

        self.client_socket.close()


if __name__ == '__main__':
    # set_up_logging('sender1.log')

    # server_ip is either host name (resolved by OS DNS) or IP address
    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]

    sender = Sender(SERVER_IP, SERVER_PORT, FILE_NAME)
    sender.send_file_content()
