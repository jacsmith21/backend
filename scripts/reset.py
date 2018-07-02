import json
import os

from pymongo import MongoClient

import config

print('Dropping the collection!')
client = MongoClient(host=config.db.uri)
db = client[config.db.name]
db.drop_collection('courses')
db.drop_collection('benchmarks')

print('Initializing the collection!')
directory = os.path.dirname(__file__)
with open(os.path.join(directory, 'data.json')) as fp:
    courses = json.load(fp)
courses = list(courses.values())[:15]

collection = db.benchmarks
benchmarks = ['Benchmark 1.0', 'Benchmark 1.1', 'Benchmark 1.2', 'Benchmark 1.3', 'Benchmark 2.0']
benchmarks = [{'name': name} for name in benchmarks]
ids = collection.insert_many(benchmarks).inserted_ids
assert collection.count() == len(benchmarks)
print('Inserted {} benchmarks'.format(len(benchmarks)))

print('Adding test benchmarks!')
for course, benchmark_id in zip(courses, ids):
    course['benchmarks'] = [benchmark_id]
courses[0]['benchmarks'].append(ids[1])

collection = db.courses
collection.insert_many(courses)
assert collection.count() == len(courses)
print('Inserted {} courses!'.format(len(courses)))

print('Finished')
