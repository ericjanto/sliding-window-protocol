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


# Returns d[a: b]
def slice_dictionary(d, a, b):
    return {k: d[k] for k in d.keys() if k in range(a, b)}


def current_window_to_string(base_seq, next_seq, window_size):
    sidebar = '|'
    sent_indicator = '>'
    next_seq_indicator = '↑'

    packet_string = sidebar
    indicator_string = sidebar

    for i in range(base_seq, base_seq + window_size):
        packet_string += f' {i} '
        packet_string += sidebar

        digit_num = len(f'{i}')
        if i < next_seq:
            indicator_string += f' {sent_indicator}'
        elif i == next_seq:
            indicator_string += f' {next_seq_indicator}'
        else:
            indicator_string += '  '

        for k in range(digit_num):
            indicator_string += ' '

        indicator_string += sidebar

    packet_string += '\n'
    indicator_string += '\n'

    top = ''
    for i in range(len(packet_string) - 1):
        top += '–'
    top += '\n'

    bottom = ''
    for i in range(len(packet_string) - 1):
        bottom += '–'
    bottom += '\n'

    return top + packet_string + indicator_string + bottom
