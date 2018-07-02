from flask import Flask
from flask import jsonify
from flask_pymongo import PyMongo
import flask_cors

import config
import crud
import parser

app = Flask(__name__)

app.config['MONGO_DBNAME'] = config.db.name
app.config['MONGO_URI'] = config.db.uri

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
        course = course['current']
        parsed.append({
            'name': course['name'],
            'prereqTree': to_dict(course['prerequisites']),
            'coreqTree': to_dict(course['corequisites'])
        })

    return jsonify(parsed)


if __name__ == '__main__':
    app.run()
