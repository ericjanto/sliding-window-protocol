import os
import threading
import time

from FrameworkRunner import FrameworkTest


def run_sim(test_results_file_name, window_size, delay_ms):
    # Simulate link layer via loopback interface
    os.system('sudo tc qdisc del dev lo root')
    os.system(f'sudo tc qdisc add dev lo root netem loss 5% delay {delay_ms}ms rate 10mbit')

    n = 2
    sender_no = 3
    receiver_no = 3
    receive_file_name = 'rfile3.jpg'
    retry_timout = 25
    test = threading.Thread(target=FrameworkTest.run_n_times,
                            args=(n, sender_no, receiver_no, receive_file_name, retry_timout, window_size,
                                  test_results_file_name))
    test.start()
    test.join()
    time.sleep(1)


def test_varied_window_sizes():
    test_fn = '_results_test_gbn.txt'

    # Create or reset output file
    with open(test_fn, 'w') as f:
        f.truncate(0)

    delay = 10

    window_sizes = [1 << exponent for exponent in range(5)]
    for ws in window_sizes:
        run_sim(test_fn, ws, delay)

    assert os.stat(test_fn).st_size == 0


def test_varied_delay_times():
    test_fn = '_results_test_gbn.txt'

    # Create or reset output file
    with open(test_fn, 'w') as f:
        f.truncate(0)

    delays = range(5, 50, 5)
    window_size = 4

    for d in delays:
        run_sim(test_fn, window_size, d)

    assert os.stat(test_fn).st_size == 0


def test_varied_all():
    test_fn = '_results_test_gbn.txt'

    # Create or reset output file
    with open(test_fn, 'w') as f:
        f.truncate(0)

    delays = range(5, 15, 5)

    window_sizes = [1 << exponent for exponent in range(3)]

    for ws in window_sizes:
        for d in delays:
            run_sim(test_fn, ws, d)

    assert os.stat(test_fn).st_size == 0
