import datetime
import time

from dateutil.relativedelta import relativedelta


time_format = '%Y-%m-%d %H:%M'


def get_curr_date():
    ts = time.time()
    return (datetime.datetime.fromtimestamp(ts))


def get_curr_date_str():
    return get_curr_date().strftime(time_format)


def str_to_time(str):
    return datetime.datetime.strptime(str, time_format)


def time_to_str(time):
    return time.strftime(time_format)


def time_add(time, months=0):
    return time + relativedelta(months=months)
