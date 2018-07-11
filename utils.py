import re
import datetime

EPOCH = datetime.datetime.utcfromtimestamp(0)
FORMAT = '%Y-%m-%d'


def split(delimiters, string, maxsplit=0, keep=False):
    delimiters = map(re.escape, delimiters)
    pattern = '|'.join(delimiters)

    if keep:
        pattern = '({})'.format(pattern)

    substrings = re.split(pattern, string, maxsplit, flags=re.IGNORECASE)
    return [substring.strip() for substring in substrings]


def format_json(json):
    return {
        'current': json,
        'base': json,
        'patch': []
    }


def unix_time(dt: datetime.datetime):
    return int((dt - EPOCH).total_seconds())


def unix_to_date(time: int):
    return datetime.datetime.utcfromtimestamp(time).strftime(FORMAT)


def date_to_datetime(date):
    return datetime.datetime.strptime(date, FORMAT)


def datetime_to_date(dt: datetime.datetime):
    return dt.strftime(FORMAT)
