import re
import datetime

EPOCH = datetime.datetime.utcfromtimestamp(0)


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


def date_to_datetime(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d')
