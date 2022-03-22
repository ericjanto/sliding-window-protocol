import os
import time
from multiprocessing import Process


class FrameworkTest:
    @staticmethod
    def run_sender(sender_no, retry_timeout):
        os.system(f'python3 Sender{sender_no}.py localhost 5555 sfile.jpg {retry_timeout}')

    @staticmethod
    def run_receiver(receiver_no, receive_file_name):
        os.system(f'python3 Receiver{receiver_no}.py 5555 {receive_file_name}')

    @staticmethod
    def run_n_times(n, sender_no, receiver_no, receive_file_name, retry_timeout, test_results_file_name):
        for i in range(n):
            print(f'Iteration: {i}')
            receiver = Process(target=FrameworkTest.run_receiver,
                               args=(receiver_no, receive_file_name,))
            sender = Process(target=FrameworkTest.run_sender,
                             args=(sender_no, retry_timeout,))
            receiver.start()
            sender.start()
            receiver.join()
            sender.join()

            time.sleep(1)

            command = f'cmp {receive_file_name} sfile.jpg'
            os.system(f'{command} | tee -a {test_results_file_name}')
