import logging
import os


def set_up_logging(log_filename):
    # Directory to save log files to
    log_dir = os.path.join(os.getcwd(), 'logs')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(log_dir, log_filename),
                        filemode='w')
