class DotDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


db = DotDict(name='curriculummapping', uri='mongodb://localhost:27017/curriculummapping')
