import os
import threading
import time

from FrameworkRunner import FrameworkTest


def run_sim(test_results_file_name):
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
    window_size = ''
    rcv_window_size = ''
    test = threading.Thread(target=FrameworkTest.run_n_times,
                            args=(n, sender_no, receiver_no, receive_file_name, retry_timeout, window_size,
                                  rcv_window_size, test_results_file_name,))
    test.start()
    test.join()
    time.sleep(1)


def test_no_diff():
    test_results_file_name = '_results_test_framework.txt'
    run_sim(test_results_file_name)
    assert os.stat(test_results_file_name).st_size == 0
