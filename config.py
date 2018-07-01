import os


class DotDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/curriculummapping')
db = DotDict(name=os.path.basename(uri), uri=uri)
ssl = ('ssl/fullchain.pem', 'ssl/privkey.pem')
