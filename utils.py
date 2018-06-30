import re


def split(delimiters, string, maxsplit=0, keep=False, keep_spaces=False):
    delimiters = map(re.escape, delimiters)
    pattern = '|'.join(delimiters)

    if keep:
        pattern = '({})'.format(pattern)

    if not keep_spaces:
        pattern = '\s*{}\s*'.format(pattern)

    return re.split(pattern, string, maxsplit, flags=re.IGNORECASE)
