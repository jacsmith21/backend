import os


# noinspection PyPep8Naming
class dot(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/curriculummapping')
db = dot(name=os.path.basename(uri), uri=uri)
secret_key = os.environ.get('SECRET_KEY', 'sajfdklsdjflkdsja')
