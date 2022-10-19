import datetime


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
