import json

from pymongo import MongoClient

import config

print('Dropping the collection!')
client = MongoClient(host=config.db.uri)
db = client[config.db.name]
db.drop_collection('courses')
db.drop_collection('benchmarks')

print('Initializing the collection!')
with open('data.json') as fp:
    courses = json.load(fp)
courses = list(courses.values())

collection = db.courses
collection.insert_many(courses)
assert collection.count() == len(courses)
print('Inserted {} courses!'.format(len(courses)))

collection = db.benchmarks
benchmarks = ['Benchmark 1.0', 'Benchmark 1.1', 'Benchmark 1.2', 'Benchmark 1.3', 'Benchmark 2.0']
benchmarks = [{'name': name} for name in benchmarks]
collection.insert_many(benchmarks)
assert collection.count() == len(benchmarks)
print('Inserted {} benchmarks'.format(len(benchmarks)))

print('Finished')
