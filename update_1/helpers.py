import datetime


def datetime_range(start, end, delta, df):
    _format = "%H:%M:%S"
    start_of_day = datetime.datetime.strptime('00:00:00', _format)
    end_of_day = datetime.datetime.strptime('23:59:59', _format)
    result = df

    current = start_of_day

    for j in range(len(df)):
        if start <= current < end:
            result[j] = 1
        current += delta
    return result
