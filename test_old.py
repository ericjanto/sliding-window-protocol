import os
import threading
import time
from multiprocessing import Process


class OldTest:
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

            receiver = Process(target=OldTest.run_receiver,
                               args=(receiver_no, receive_file_name,))
            sender = Process(target=OldTest.run_sender,
                             args=(sender_no, retry_timeout,))
            receiver.start()
            sender.start()
            receiver.join()
            sender.join()

            time.sleep(1)

            command = f'cmp {receive_file_name} sfile.jpg'
            os.system(f'{command} | tee -a {test_results_file_name}')


if __name__ == '__main__':
    test_results_file_name = 'test_old_test.txt'

    # Simulate link layer via loopback interface
    os.system('sudo tc qdisc del dev lo root')
    os.system('sudo tc qdisc add dev lo root netem delay 10ms rate 5mbit')

    # Create or reset output file
    with open(test_results_file_name, 'w') as f:
        f.truncate(0)

    n = 10
    sender_no = 1
    receiver_no = 1
    receive_file_name = 'rfile1.jpg'
    retry_timeout = ''
    test = threading.Thread(target=OldTest.run_n_times,
                            args=(
                                n, sender_no, receiver_no, receive_file_name, retry_timeout, test_results_file_name,))
    test.start()
    test.join()
    time.sleep(1)
