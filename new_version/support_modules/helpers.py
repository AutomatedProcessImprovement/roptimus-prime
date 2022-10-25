import datetime
import itertools

def datetime_range(start, end, delta, slots):
    _format = "%H:%M:%S"
    start_of_day = datetime.datetime.strptime('00:00:00', _format)
    end_of_day = datetime.datetime.strptime('23:59:59', _format)
    slots = slots
    res = '0b'

    current = start_of_day
    for j in range(slots):
        if start <= current < end:
            res += '1'
        else:
            res += '0'
        current += delta
    return int(res, 2)


def sum_of_binary_ones(num):
    return sum(map(int, "{0:b}".format(num)))


def _calculate_shifts(num):
    shifts = [(k, len(list(v))) for k, v in itertools.groupby(str(bin(num)[2:]))]
    shifts_of_day = int(len(shifts) / 2)
    return shifts_of_day


def _get_consecutive_shift_lengths(num):
    shifts = [(int(k), len(list(v))) for k, v in itertools.groupby(str(bin(num)[2:]))]
    return shifts


def _bitmap_to_valid_structure(bitmap, num_slots):
    bit_str = bin(bitmap)[2:]
    blank_out = (num_slots * 24) * '0'
    out = blank_out[:len(blank_out) - len(bit_str)] + bit_str
    return [int(x) for x in out]


def _list_to_binary(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out
