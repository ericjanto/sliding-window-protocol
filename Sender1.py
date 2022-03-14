from fileinput import filename
from socket import *
import sys
import os
from time import sleep

# server_ip is either host name (resolved by OS DNS) or IP address
server_ip = sys.argv[1]
server_port = int(sys.argv[2])
file_name = sys.argv[3]

# Set up client socket
client_socket = socket(AF_INET, SOCK_DGRAM)

# Get file from OS and split into packets
# Is this the payload size you want? Or should I subtract the header? TODO
HEADER_SIZE = 3
PAYLOAD_SIZE = 1024

payloads = {}
seq = 0
start = 0
stop = PAYLOAD_SIZE

# Read into packets
with open(file_name, 'rb') as f:
    file_content = bytearray(f.read())

# I'm sure there is a more elegant way to do this
while start <= len(file_content):
    # For last package: only send file content leftovers
    if stop > len(file_content):
        stop = len(file_content)

    payload = file_content[start:stop]
    payloads[seq] = payload

    if stop == len(file_content):
        # Terminate while loop
        start = len(file_content) + 1
    else:
        start = stop

    stop += PAYLOAD_SIZE
    seq += 1

# TODO: Maybe need to make sure that last package still 1027 bytes, not only file contents?
# See: https://piazza.com/class/kybwnkij3jf67m?cid=377

for s in payloads:
    packet = bytearray(HEADER_SIZE + PAYLOAD_SIZE)
    header = bytearray(HEADER_SIZE)

    seq_in_byte = bytearray(s.to_bytes(2, byteorder='big'))

    eof = 1 if s == seq - 1 else 0
    eof_in_byte = bytearray(eof.to_bytes(1, byteorder='big'))

    header[0] = seq_in_byte[0]
    header[1] = seq_in_byte[1]
    header[2] = eof_in_byte[0]

    packet[0] = header[0]
    packet[1] = header[1]
    packet[2] = header[2]
    packet[3:] = payloads[s]

    client_socket.sendto(packet, (server_ip, server_port))
    
    # Prevent packet loss due to internal OS buffering
    sleep(0.01)

client_socket.close()