from flask import Flask
from flask import jsonify
from flask_pymongo import PyMongo
import flask_cors

import crud
import parser

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'curriculummapping'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/curriculummapping'

flask_cors.CORS(app)

mongo = PyMongo(app)

crud.crud(app, mongo, 'courses')
crud.crud(app, mongo, 'benchmarks')


@app.route('/', methods=['GET'])
def root():
    return 'Welcome to Jacob\'s application. This is the API!'


@app.route('/parse', methods=['GET'])
def parse():
    def to_dict(expression):
        tree = parser.parse(expression)
        if tree is None:
            return None
        else:
            return tree.to_dict()

    parsed = []
    for course in mongo.db.courses.find():
        parsed.append({
            'name': course['name'],
            'prereqTree': to_dict(course['prerequisites']),
            'coreqTree': to_dict(course['corequisites'])
        })

    return jsonify(parsed)


@app.route('/parse/<name>', methods=['GET'])
def parse_course(name):
    course = mongo.db.courses.find_one({'name': name})
    prerequisites = parser.parse(course['prerequisites'])
    if prerequisites is None:
        prerequisite_tree = None
    else:
        prerequisite_tree = prerequisites.to_dict()
    return jsonify(prerequisite_tree)


if __name__ == '__main__':
    app.run()
