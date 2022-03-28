# Size of seq number, in bytes.
SEQ_SIZE = 2

# Size of eof flag, in bytes.
EOF_SIZE = 1

# Size of packet header, in bytes.
HEADER_SIZE = SEQ_SIZE + EOF_SIZE

# Size of packet payload, in bytes.
PAYLOAD_SIZE = 1024

# Buffer size for received messages, in bytes.
BUFFER_SIZE = HEADER_SIZE + PAYLOAD_SIZE

# Size of ack message
ACK_SIZE = 2

# Buffer size for ack messages
ACK_BUFFER_SIZE = ACK_SIZE

# Time after which sockets are closed if no messages are transferred
# anymore
TERMINATION_TIMEOUT = 5
