# Eric Janto s1975761
# Util class to handle byte <-> int conversions

from constants import EOF_SIZE, SEQ_SIZE


def int_to_bytearray(x, store_in_n_bytes):
    return bytearray(x.to_bytes(store_in_n_bytes, byteorder='big'))


def bytearray_to_int(ba):
    return int.from_bytes(ba, 'big')


def seq_byte_to_int(seq_byte):
    return bytearray_to_int(seq_byte)


def seq_int_to_byte(seq_int):
    return int_to_bytearray(seq_int, SEQ_SIZE)


def eof_byte_to_int(eof_byte):
    return bytearray_to_int(eof_byte)


def eof_int_to_byte(eof_int):
    return int_to_bytearray(eof_int, EOF_SIZE)
