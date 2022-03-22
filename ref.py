import logging
from Sender1 import Sender
import sys
from socket import *
import time


class Sender2(Sender):
    def __init__(self, host, port, file_name, timeout):
        super(Sender2, self).__init__(host, port, file_name)
        self.timeout = int(timeout)/1000
        logging.basicConfig(level=logging.DEBUG, filename='sender2.log')

    def get_size(self):
        file_data = self.read_file(self.file_name)
        return len(file_data)

    def send_file(self):
        re_trans = 0
        buffer = 2
        file_data = self.read_file(self.file_name)
        pac_lis = self.add_header(self.file_to_packet(file_data))
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(self.timeout)
        dst_addr = (self.host, self.port)
        time_start = float(time.perf_counter())
        for i in range(len(pac_lis)):
            s.sendto(pac_lis[i], dst_addr)
            logging.debug('Sent pkt {0}'.format(i))
            while True:
                try:
                    ack_b, addr = s.recvfrom(buffer)
                    ack = int.from_bytes(ack_b, 'big')
                    logging.debug('Receive ack {0}'.format(ack))
                except timeout:
                    logging.debug('Detect Timeout')
                    ack = 'timeout'
                if ack == i:
                    logging.debug('Accept ack {0}'.format(ack))
                    break
                elif ack == 'timeout':
                    logging.debug('ReSend pkt {0}'.format(i))
                    re_trans += 1
                    s.sendto(pac_lis[i], dst_addr)
                else:
                    logging.debug('Duplicate ack {0}'.format(i))
        s.close()
        time_end = float(time.perf_counter())
        total_bytes = self.get_size()
        print(re_trans, (total_bytes/1000)/(time_end - time_start))


if __name__ == '__main__':
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    TIMEOUT = sys.argv[4]

    sender2 = Sender2(HOST, PORT, FILE_NAME, TIMEOUT)
    sender2.send_file()