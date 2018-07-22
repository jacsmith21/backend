import contextlib
import functools
import http
import os
import re
import datetime
import tempfile

import flask
import flask_pymongo
import jwt
import openpyxl

import config

EPOCH = datetime.datetime.utcfromtimestamp(0)
FORMAT = '%Y-%m-%d'
EXPORT_MAP = {
    'number': 'C3',
    'title': 'C4',
    'link': 'C5',
    'caebAttributes.knowledgeBase': 'C13',
    'caebAttributes.problemAnalysis': 'D13',
    'caebAttributes.investigation': 'E13',
    'caebAttributes.design': 'F13',
    'caebAttributes.tools': 'G13',
    'caebAttributes.team': 'H13',
    'caebAttributes.communication': 'I13',
    'caebAttributes.professionalism': 'J13',
    'caebAttributes.impacts': 'K13',
    'caebAttributes.ethics': 'L13',
    'caebAttributes.economics': 'M13',
    'caebAttributes.ll': 'N13',
    'auDistribution.math': 'E11',
    'auDistribution.naturalScience': 'G11',
    'auDistribution.complementaryStudies': 'I11',
    'auDistribution.engineeringScience': 'K11',
    'auDistribution.engineeringDesign': 'M11'
}


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


def authenticate(mongo: flask_pymongo.PyMongo):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            token = flask.request.headers.get('Authorization')

            try:
                data = jwt.decode(token, config.secret_key)
                user = mongo.db.users.find_one({'username': data['sub']})
                if not user:
                    raise RuntimeError('User not found')
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return flask.jsonify({'message': 'Expired token. Re-authentication required.'}), http.HTTPStatus.UNAUTHORIZED
            except jwt.InvalidTokenError:
                return flask.jsonify({'message': 'Invalid token. Registration and / or authentication required'}), http.HTTPStatus.UNAUTHORIZED
        return wrapper
    return decorator


@contextlib.contextmanager
def export(course):
    with tempfile.TemporaryDirectory() as tempdir:
        src = os.path.join(os.path.dirname(__file__), 'base.xlsm')
        dst = os.path.join(tempdir, '{}.xlsm'.format(course['number']))

        workbook = openpyxl.load_workbook(src)
        sheet = workbook['CSE_Shortlist']
        sheet.title = course['number']

        for key in course:
            sheet[EXPORT_MAP[key]] = course[key]

        workbook.save(dst)
        workbook.close()

        yield dst
