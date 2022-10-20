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
