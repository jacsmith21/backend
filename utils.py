import re


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
