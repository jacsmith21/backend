import json
import os
import time

import jsonpatch
from pymongo import MongoClient

import config
import utils

print('Dropping the collection!')
client = MongoClient(host=config.db.uri)
db = client[config.db.name]
db.drop_collection('courses')
db.drop_collection('benchmarks')

print('Initializing the collection!')
directory = os.path.dirname(__file__)
with open(os.path.join(directory, 'data.json')) as fp:
    courses = json.load(fp)
courses = list(courses.values())[:15]  # lets just put in 15 for now
courses = [utils.format_json(course) for course in courses]

collection = db.benchmarks
benchmarks = ['Benchmark 1.0', 'Benchmark 1.1', 'Benchmark 1.2', 'Benchmark 1.3', 'Benchmark 2.0']
benchmarks = [{'name': name} for name in benchmarks]
benchmarks = [utils.format_json(benchmark) for benchmark in benchmarks]
ids = collection.insert_many(benchmarks).inserted_ids
assert collection.count() == len(benchmarks)
print('Inserted {} benchmarks'.format(len(benchmarks)))

print('Adding test benchmarks relationships!')
for course, benchmark_id in zip(courses, ids):
    course['base']['benchmarks'] = [benchmark_id]
courses[0]['base']['benchmarks'].append(ids[1])

for course, _ in zip(courses, ids):
    course['current'] = course['base']

course = courses[0]
src = course['base']
dst = src.copy()
dst['maintainer'] = 'Jacob'
dst['title'] = 'Patching Title'
del dst['description']
now = time.time()
day = 24*60*60
timestamps = [now - 2 * day, now - day, now]
course['patch'] = \
    [{**operation, 'time': timestamp} for operation, timestamp in zip(jsonpatch.make_patch(src, dst), timestamps)]
course['current'] = dst
print('Adding fake patches to {}'.format(src['name']))

collection = db.courses
collection.insert_many(courses)
assert collection.count() == len(courses)
print('Inserted {} courses!'.format(len(courses)))

print('Finished')
