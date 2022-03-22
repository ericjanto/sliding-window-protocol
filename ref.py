import logging
import threading

from Receiver1 import Receiver
import sys
from socket import *


class Receiver2(Receiver):

    def receive_file(self):
        seq_lis = []
        content = bytes(0)
        localhost = '127.0.0.1'
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((localhost, self.port))
        seq_expect = 0

        last = threading.Event()
        while True:
            data, addr = s.recvfrom(self.buffer)
            seq = self.get_seq(data)
            # logging.debug('Received pkt {0}'.format(seq))
            if seq not in seq_lis:
                if seq == seq_expect:
                    seq_lis.append(seq)
                    content += self.remove_header(data)
                    seq_expect += 1
                    # logging.debug('Accept pkt {0}'.format(seq))
                # elif seq != seq_expect:
                    # logging.debug('Discard pkt {0}'.format(seq))
            # else:
                # logging.debug('Detect Duplication pkt {0}'.format(seq))
            s.sendto(seq.to_bytes(2, 'big'), addr)
            # logging.debug('Send ack {0}'.format(seq_lis[-1]))
            if self.get_eof(data) == 1:
                while True:
                    try:
                        s.settimeout(3)
                        data, addr = s.recvfrom(self.buffer)
                        seq = self.get_seq(data)
                        s.sendto(seq.to_bytes(2, 'big'), addr)
                        # logging.debug('Send ack {0}'.format(seq_lis[-1]))
                    except timeout:
                        break
                break
        s.close()
        file = open(self.file_name, 'wb')
        # logging.debug('write file {0}'.format(self.file_name))
        file.write(content)


if __name__ == '__main__':
    PORT = int(sys.argv[1])
    FILE_NAME = sys.argv[2]

    # logging.basicConfig(level=logging.INFO, filename='receiver2.log')

    receiver2 = Receiver2(PORT, FILE_NAME)
    receiver2.receive_file()