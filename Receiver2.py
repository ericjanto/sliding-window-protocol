# Eric Janto s1975761
from socket import *
import sys

server_port = int(sys.argv[1])
file_name = sys.argv[2]

# Set up the server socket
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))


# Checks whether a received packet is a retransmission
# Do this by checking whether its SEQ is different to the
# most recently received packet SEQ, or the same
def is_duplicate(received_packet):
    # TODO: maybe need to handle duplicate packets at some point,
    # But atm duplicates just replace packets in the dictionary
    # so duplicates are never written to a file multiple times
    pass


def int_to_bytearray(x, store_in_n_bytes):
    return bytearray(x.to_bytes(store_in_n_bytes, byteorder='big'))


def bytearray_to_int(ba, number_of_fields):
    # number_of_fields specified index - 1 until which we add
    return int.from_bytes(ba[0:number_of_fields], 'big')


# Sends an ACKnowledgement message to the sender
def send_ACK(seq, client_address):
    # Create ACK (2 bytes = 16-bit seq number)
    # This can just be the seq of the received packet
    ack = int_to_bytearray(seq, 2)
    server_socket.sendto(ack, client_address)
    pass


def receive_packets():
    # Receive packets
    packets = {}
    while True:
        # client_address is client IP and port
        message, client_address = server_socket.recvfrom(2048)
        header = message[0:3]
        seq = bytearray_to_int(header, 2)
        eof = header[2]

        packet = message[3:]
        packets[seq] = packet
        send_ACK(seq, client_address)

        if eof == 1:
            send_ACK(seq, client_address)
            send_ACK(seq, client_address)
            send_ACK(seq, client_address)
            break

    server_socket.close()
    return packets


def write_packets_to_file(packets):
    with open(file_name, 'wb') as transferred_file:
        for s in packets:
            transferred_file.write(packets[s])


packets_to_write = receive_packets()
write_packets_to_file(packets_to_write)
