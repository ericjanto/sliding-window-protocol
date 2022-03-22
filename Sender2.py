# Eric Janto s1975761
from socket import *
import sys

from CustomTimer import *

# server_ip is either host name (resolved by OS DNS) or IP address
server_ip = sys.argv[1]
server_port = int(sys.argv[2])
file_name = sys.argv[3]
# Positive integer in ms
retry_timeout = int(sys.argv[4])

# Set up client socket
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(retry_timeout / 1000)

HEADER_SIZE = 3
PAYLOAD_SIZE = 1024

global_timer = CustomTimer()


def extract_payloads(content):
    payloads_l = {}
    seq = 0

    # I'm sure there is a more elegant way to do this
    start = 0
    stop = PAYLOAD_SIZE
    while start <= len(content):
        # For last package: only send file content leftovers
        if stop > len(content):
            stop = len(content)

        payload = content[start:stop]
        payloads_l[seq] = payload

        if stop == len(content):
            # Terminate while loop
            start = len(content) + 1
        else:
            start = stop

        stop += PAYLOAD_SIZE
        seq += 1

    return payloads_l


# I could definitely do the below in extract_payloads
def assemble_packets(payloads_l):
    packets_l = {}

    for s in payloads_l:
        packet = bytearray(HEADER_SIZE + PAYLOAD_SIZE)
        header = bytearray(HEADER_SIZE)

        seq_in_byte = int_to_bytearray(s, 2)

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


def int_to_bytearray(x, store_in_n_bytes):
    return bytearray(x.to_bytes(store_in_n_bytes, byteorder='big'))


def send_packets(packets_l):
    number_retransmissions = 0
    transmission_time = 0
    global_timer.start_timer()
    for s in packets_l:
        success = False
        resent = 0
        while not success:
            # TODO: remove print statement
            # print(f'Sending packet {s}. Attempt: {resent}.')
            client_socket.sendto(packets_l[s], (server_ip, server_port))

            try:
                message, _ = client_socket.recvfrom(2048)
                if is_ACK(s, message):
                    success = True
                    # If last ACK:
                    if s == len(packets_l) - 1:
                        transmission_time = global_timer.get_current_timer_value()
            except error:
                # print('Resending file because ACK not received within time window.')
                resent += 1

        number_retransmissions += resent
    return number_retransmissions, transmission_time


def bytearray_to_int(ba, number_of_fields):
    return int.from_bytes(ba[0:number_of_fields], 'big')


# Checks whether a package transfer is ACKnowledged
def is_ACK(current_seq, received_ack_packet):
    rap_int = bytearray_to_int(received_ack_packet, 2)
    return current_seq == rap_int


def calculate_throughput(total_time_in_s, datasize_in_bytes):
    # Factor of (1000) since we want to output in kilobytes/s
    return (datasize_in_bytes / 1000) / total_time_in_s


# Read into packets
with open(file_name, 'rb') as f:
    file_content = bytearray(f.read())

payloads = extract_payloads(file_content)
packets = assemble_packets(payloads)
retransmissions, time_to_send = send_packets(packets)
throughput = round(calculate_throughput(time_to_send, len(file_content)), 2)

print(f'{retransmissions} {throughput}')
