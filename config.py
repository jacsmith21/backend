import os


# noinspection PyPep8Naming
import random
import string
import uuid


# noinspection PyPep8Naming
class dot(dict):
    def __getattr__(self, key):
        return self[key]


_HERE = os.path.dirname(__file__)
_SECRET_PATH = os.path.join(_HERE, 'SECRET_KEY')
_CODE_PATH = os.path.join(_HERE, 'CODE')

if os.path.exists(_SECRET_PATH):
    with open(_SECRET_PATH) as _fp:
        secret_key = _fp.read()
else:
    secret_key = str(uuid.uuid4())
    with open(_SECRET_PATH, 'w') as _fp:
        _fp.write(secret_key)


if 'CODE' in os.environ:
    code = os.environ.get('CODE')
else:
    if os.path.exists(_CODE_PATH):
        with open(_CODE_PATH) as _fp:
            code = _fp.read()
    else:
        code = random.choices(string.ascii_uppercase + string.digits, k=6)
        code = ''.join(code)
        with open(_CODE_PATH, 'w') as _fp:
            _fp.write(code)


uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/curriculummapping')
db = dot(name=os.path.basename(uri), uri=uri)
