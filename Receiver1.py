from fileinput import filename
from socket import *
import sys

server_port = int(sys.argv[1])
file_name = sys.argv[2]

# Set up the server socket
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))

# Receive packets
packets = {}
with open(file_name, 'wb') as transferred_file:
    while True:
        # client_address is client IP and port
        message, client_address = server_socket.recvfrom(2048)
        # print(len(message))
        # Need to remove header
        header = message[0:3]
        # seq = int.from_bytes(header[0] + header[1], 'big')
        eof = header[2]

        packet = message[3:]
        packets[0] = packet # todo: change 0 to seq if seq correct

        transferred_file.write(packet)

        if eof == 1:
            break

server_socket.close()