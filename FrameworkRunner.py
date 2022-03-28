import os
import time
from multiprocessing import Process


class FrameworkTest:
    @staticmethod
    def run_sender(sender_no, retry_timeout, window_size):
        os.system(f'python3 Sender{sender_no}.py localhost 5555 sfile.jpg {retry_timeout} {window_size}')

    @staticmethod
    def run_receiver(receiver_no, receive_file_name, rcv_window_size):
        os.system(f'python3 Receiver{receiver_no}.py 5555 {receive_file_name} {rcv_window_size}')

    @staticmethod
    def run_n_times(n, sender_no, receiver_no, receive_file_name, retry_timeout, window_size, rcv_window_size,
                    test_results_file_name):
        for i in range(n):
            print(f'Iteration: {i}')
            receiver = Process(target=FrameworkTest.run_receiver,
                               args=(receiver_no, receive_file_name, rcv_window_size,))
            sender = Process(target=FrameworkTest.run_sender,
                             args=(sender_no, retry_timeout, window_size))
            receiver.start()
            sender.start()
            receiver.join()
            sender.join()

            command = f'cmp {receive_file_name} sfile.jpg'
            os.system(f'{command} | tee -a {test_results_file_name}')

            time.sleep(1)
