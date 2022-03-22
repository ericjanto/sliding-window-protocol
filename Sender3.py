# Eric Janto s1975761

from CustomTimer import *

import sys
import time
import threading

class Sender3:
    def __init__(self, server_ip, server_port, file_name, retry_timeout, window_size):
        self.server_ip = server_ip
        self.server_pot = server_port
        self.file_name = file_name
        self.retry_timeout = retry_timeout
        self.window_size = window_size

        # Sequence number of the oldest unacknowledged packet
        self.base_seq = 0

        # The smallest unused sequence number, so the number of the next packet to be sent
        self.next_seq_num = 0

    # As opposed to how the book suggests it, this
    # method does not only send a single packet but
    # the entire file.
    def rdt_send(self):
        timer = CustomTimer()
        timer.start_timer()
        pass

if __name__ == '__main__':
    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    RETRY_TIMEOUT = int(sys.argv[4])
    WINDOW_SIZE = int(sys.argv[5])

    sender = Sender3(SERVER_IP, SERVER_PORT, FILE_NAME, RETRY_TIMEOUT, WINDOW_SIZE)
    sender.rdt_send()
