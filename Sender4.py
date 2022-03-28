import logging
import sys
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor

from Sender3 import Sender3
from constants import ACK_BUFFER_SIZE
from conversions import bytearray_to_int
#from utils import set_up_logging


class Sender4(Sender3):
    def __init__(self, server_ip, server_port, file_name, timeout_ms, window_size):
        super(Sender4, self).__init__(server_ip, server_port, file_name, timeout_ms, window_size)

        # Holds seqs of packets which are currently in the window
        self.current_window = []

        # Holds seqs of packets that are in the window but have yet to be sent
        self.current_window_to_be_sent = []

        # Keep track of packets that have been received successfully.
        self.sent_and_received = []

    # Sends packet using an own thread as every packet
    # needs its own timer now.
    def send_single_packet(self, packet_seq):
        #logging.debug(f'Sending packet {packet_seq}.')
        self.client_socket.sendto(self.packets[packet_seq], self.client_address)
        self.resend_packet_on_timeout(packet_seq)
        self.sent_and_received.append(packet_seq)
        #logging.debug(f'Packet {packet_seq} sent and received.')

    def resend_packet_on_timeout(self, packet_seq):
        packet_removed_from_window = threading.Event()

        check = threading.Thread(target=self.check_removed_from_window, args=(packet_seq, packet_removed_from_window))
        check.setDaemon(True)
        check.start()

        # As long as the packet is in the window, keep resending it if a timeout occurs
        while True:
            if not packet_removed_from_window.wait(timeout=self.timeout):
                #logging.debug(f'Resending packet {packet_seq}, no ACK received for it within timeout.')
                self.client_socket.sendto(self.packets[packet_seq], self.client_address)
            else:
                break

    def check_removed_from_window(self, pkt, packet_removed_from_window):
        while True:
            with self.lock:
                if pkt not in self.current_window:
                    packet_removed_from_window.set()
            # This check only needs to occur within a realistic time
            # a packet could actually have been removed from the window,
            # which is at most (!) the retry timeout. To be safe, choose a value
            # lower than the timeout.
            time.sleep(self.timeout * 0.25)

    def receiver_ack_sender4(self):
        while True:
            ack = bytearray_to_int(self.client_socket.recv(ACK_BUFFER_SIZE))
            #logging.debug(f'Received ack {ack}.')

            with self.lock:
                self.update_window_sender4(ack)

    def update_window_sender4(self, ack):
        if self.ack_in_window(ack):
            self.remove_packet_from_window(ack)
            # If ACK is same as base_seq, need to establish new base_seq for window
            if ack == self.base_seq:
                self.forward_window_base()
            self.forward_window_end()

    def forward_window_base(self):
        # If no packets in window, jump window to next packet to be sent
        if not self.current_window:
            self.base_seq = self.next_seq
        # Otherwise, set it to the lowest packet in the window
        else:
            self.base_seq = self.current_window[0]

    def forward_window_end(self):
        while self.next_seq < self.base_seq + self.window_size:
            self.add_packet_to_window(self.next_seq)
            self.add_packet_to_to_be_sent(self.next_seq)
            self.next_seq += 1

    # Checks whether an ACK is for a packet in the current window.
    # Since window might be updated when base_seq is not updated, having
    # those two conditions is a relevant safety measure
    def ack_in_window(self, ack):
        in_updated_window = ack in range(self.base_seq, self.base_seq + self.window_size)
        in_current_window = ack in self.current_window
        return in_current_window and in_updated_window

    # Safely adds packet to window whilst maintaining packet order
    def add_packet_to_window(self, packet_seq):
        #logging.debug(f'Adding packet {packet_seq} to window.')
        #logging.debug(f'Window: {self.current_window}')
        self.current_window.append(packet_seq)
        self.current_window.sort()

    # Safely removes packet from window whilst maintaining packet order
    def remove_packet_from_window(self, packet_seq):
        #logging.debug(f'Removing packet {packet_seq} from window.')
        #logging.debug(f'Window: {self.current_window}')
        self.current_window.remove(packet_seq)
        self.current_window.sort()

    def add_packet_to_to_be_sent(self, packet_seq):
        #logging.debug(f'Adding packet {packet_seq} to to_be_sent.')
        #logging.debug(f'Window > to_be_sent: {self.current_window} >'
                      #f'{self.current_window_to_be_sent}')
        self.current_window_to_be_sent.append(packet_seq)
        self.current_window_to_be_sent.sort()

    def remove_packet_from_to_be_sent(self, packet_seq):
        self.current_window_to_be_sent.remove(packet_seq)
        self.current_window_to_be_sent.sort()

    def send_file_content(self):
        self.timer.start_timer()
        recv = threading.Thread(target=self.receiver_ack_sender4)
        recv.setDaemon(True)
        recv.start()

        with self.lock:
            self.forward_window_end()

        self.send_packets()

        transmission_time = self.timer.get_current_timer_value()

        throughput = round(Sender4.calculate_throughput(transmission_time, self.get_file_size()), 2)
        print(throughput)

    def all_packets_are_sent(self):
        return list(self.packets)[-1] in self.sent_and_received

    def send_packets(self):
        with ThreadPoolExecutor(max_workers=self.window_size) as tpe:
            while True:
                if self.all_packets_are_sent():
                    break
                elif self.current_window_to_be_sent:
                    with self.lock:
                        self.current_window_to_be_sent.sort()
                        remove_list = []
                        for packet_seq in self.current_window_to_be_sent:
                            logging.debug(f'Before submitting: {self.current_window_to_be_sent}')
                            logging.debug(f'Submitting packet {packet_seq} to be sent.')
                            tpe.submit(self.send_single_packet, packet_seq)
                            remove_list.append(packet_seq)
                            logging.debug(f'After submitting: {self.current_window_to_be_sent}')

                        for packet_seq in remove_list:
                            self.remove_packet_from_to_be_sent(packet_seq)
                # Only need to run this while loop within an interval
                # where changes can actually happen, i.e. within timeout window.
                time.sleep(self.timeout * 0.1)


if __name__ == '__main__':
    #set_up_logging('sender4.log')

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    RETRY_TIMEOUT = int(sys.argv[4])
    WINDOW_SIZE = int(sys.argv[5])

    sender = Sender4(SERVER_IP, SERVER_PORT, FILE_NAME, RETRY_TIMEOUT, WINDOW_SIZE)
    sender.send_file_content()
