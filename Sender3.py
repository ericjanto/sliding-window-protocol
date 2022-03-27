# Eric Janto s1975761
import logging
import sys
import threading
from threading import Lock

from Sender2 import Sender2
from constants import ACK_BUFFER_SIZE
from conversions import bytearray_to_int
from utils import current_window_to_string, set_up_logging, slice_dictionary


class Sender3(Sender2):
    def __init__(self, server_ip, server_port, file_name, timeout_ms, window_size):
        super(Sender3, self).__init__(server_ip, server_port, file_name, timeout_ms)

        self.client_address = (self.server_ip, self.server_port)

        # Reset timeout from Sender2
        self.client_socket.settimeout(None)

        self.window_size = window_size

        file_content = self.read_file(self.file_name)
        self.packets = self.add_headers(self.get_payloads(file_content))

        # Sequence number of the oldest unacknowledged packet
        self.base_seq = 0

        # Sequence number of the next packet to be sent
        self.next_seq = 0

        # Use this to make sure that shared variables are only modified by
        # one thread at a time
        self.lock = Lock()

    # Sends packets in window.
    # Constantly running thread.
    def send_window(self, acked_tracker):
        while True:
            if self.all_packets_are_sent():
                break
            send_packets = self.to_be_sent_packets()
            if len(send_packets) > 0:
                logging.debug(f'>>! Window status:\n\n'
                              f'{current_window_to_string(self.base_seq, self.next_seq, self.window_size)}')
                logging.debug(f'>>! Sending window part [{list(send_packets.keys())[0]},'
                              f'{len(send_packets) - 1}].')
                for seq in send_packets:
                    logging.debug(f'>>>>! Sending packet {seq}.')
                    self.client_socket.sendto(send_packets[seq], self.client_address)
                    self.forward_next_seq()

            # clear() sets the internal flag of the event to false
            # so that any thread calling event.wait() will block until
            # event.set() is called and the event flag is set to true
            acked_tracker.clear()

            # Below gets triggered if the event does not get flagged
            # true (by the ack receiver thread) before the timeout value
            # is reached
            if not acked_tracker.wait(self.timeout):
                logging.debug('--! No ACK received within timeout value,'
                              'packet might be lost or delayed. Resending unacked part of window.')
                self.resend_unacked_packets()

    def all_packets_are_sent(self):
        # TODO: check if the first condition can be removed
        return self.base_seq > len(self.packets) - 1 \
               or self.next_seq > len(self.packets) - 1

    # Packets in [next_seq_num, base_seq + N] can be sent immediately.
    # Returns empty dictionary if window is full or there are no packets
    # left to be sent.
    def to_be_sent_packets(self):
        # This is the seq of the first package outwith the window
        end_of_window = self.base_seq + self.window_size
        return slice_dictionary(self.packets, self.next_seq, end_of_window)

    # Packets in [base_seq, next_seq] are packets which have been sent
    # but are yet to be acked
    def sent_but_unacked_packets(self):
        return slice_dictionary(self.packets, self.base_seq, self.next_seq)

    def forward_next_seq(self):
        # Don't move next_seq out of bounds
        if not self.next_seq >= len(self.packets) - 1:
            # self.lock is a shared variable among the threads which
            # might lead to race conditions -> need to use a lock.
            with self.lock:
                self.next_seq += 1

    # Resends send yet unacked packets.
    # Triggered when a timeout occurs which indicates a potentially lost packet.
    def resend_unacked_packets(self):
        packets = self.sent_but_unacked_packets()
        for seq in packets:
            logging.debug(f'----> Resending packet {seq}.')
            self.client_socket.sendto(packets[seq], self.client_address)
        logging.debug(f'--! Window resent.')

    # Receive ack messages from client.
    # Constantly running thread.
    def receive_ack(self, acked_tracker):
        while True:
            ack = bytearray_to_int(self.client_socket.recv(ACK_BUFFER_SIZE))
            logging.debug(f'<<! Received ack {ack}.')

            self.update_window(ack, acked_tracker)

            # All packets received at client side
            if ack == len(self.packets) - 1:
                break

    def update_window(self, ack, acked_tracker):
        with self.lock:
            # This means the oldest unacked packet is ACKed now
            # so can move the window forward by one.
            if ack == self.base_seq:
                self.forward_window()
                # Trigger acked event
                acked_tracker.set()
            # This happens when an ACK sent from the client
            # gets lost. However, since the client only sends ACKs for
            # packets in order, it is guaranteed the all packets before that
            # are received and the window can continue from the next-most packet.
            elif ack > self.base_seq:
                self.jump_window(ack)
                acked_tracker.set()

    def forward_window(self):
        self.base_seq += 1
        # TODO: maybe need to send and progress next_seq as well?
        logging.debug(f'<<-- Forwarded window, progressed base_seq to {self.base_seq}.\n\n')

    def jump_window(self, ack):
        self.base_seq = ack + 1
        # Depending on how many ACKs got lost, might
        # need to reset next_seq as well.
        if self.next_seq < self.base_seq:
            self.next_seq = self.base_seq
        logging.debug(f'<<-- Jumped window, progressed base_seq to {self.base_seq}.\n\n')

    def send_file_content(self):
        self.timer.start_timer()

        acked_trigger = threading.Event()

        sender_thread = threading.Thread(target=self.send_window,
                                         args=(acked_trigger,))
        receiver_thread = threading.Thread(target=self.receive_ack,
                                           args=(acked_trigger,))

        # TODO: check if this can be removed yet would still pass test
        sender_thread.setDaemon(True)
        receiver_thread.setDaemon(True)

        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        receiver_thread.join()

        transmission_time = self.timer.get_current_timer_value()

        self.client_socket.close()

        throughput = round(Sender3.calculate_throughput(transmission_time, self.get_file_size()), 2)
        print(throughput)


if __name__ == '__main__':
    set_up_logging('sender3.log')

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    RETRY_TIMEOUT = int(sys.argv[4])
    WINDOW_SIZE = int(sys.argv[5])

    sender = Sender3(SERVER_IP, SERVER_PORT, FILE_NAME, RETRY_TIMEOUT, WINDOW_SIZE)
    sender.send_file_content()
