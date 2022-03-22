# Eric Janto s1975761
import time


# Utility class for timing packet sending
class CustomTimer:
    def __init__(self):
        self.start_time = None
        # Timeout expected in s
        # self.timeout = timeout

    def start_timer(self):
        self.start_time = time.perf_counter()

    def reset_timer(self):
        self.start_time = time.perf_counter()

    def get_current_timer_value(self):
        return time.perf_counter() - self.start_time

    # Checks whether the timer has passed the time threshold
    def passed_time_threshold(self, time_threshold):
        # threshold is passed in ms
        threshold_in_s = time_threshold / 1000
        return self.get_current_timer_value() > threshold_in_s
