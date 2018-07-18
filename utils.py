import functools
import re
import datetime

import flask
import flask_pymongo
import jwt

import config

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


def token_required(mongo: flask_pymongo.PyMongo):
    def decorator(f):
        @functools.wraps(f)
        def _verify(*args, **kwargs):
            token = flask.request.headers.get('Authorization', '')

            invalid_msg = {
                'message': 'Invalid token. Registration and / or authentication required',
                'authenticated': False
            }
            expired_msg = {
                'message': 'Expired token. Re-authentication required.',
                'authenticated': False
            }

            # if len(auth_headers) != 2:
            #     return flask.jsonify(invalid_msg), 401

            try:
                data = jwt.decode(token, config.secret_key)
                user = mongo.db.users.find_one({'username': data['sub']})
                if not user:
                    raise RuntimeError('User not found')
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return flask.jsonify(expired_msg), 401  # 401 is Unauthorized HTTP status code
            except jwt.InvalidTokenError as e:
                return flask.jsonify(str(e)), 401
        return _verify
    return decorator
