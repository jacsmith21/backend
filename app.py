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
    parsed = {}
    for course in mongo.db.courses.find():
        prerequisites = parser.parse(course['prerequisites'])
        if prerequisites is None:
            parsed[course['name']] = None
        else:
            parsed[course['name']] = prerequisites.to_dict()
    return jsonify(parsed)


if __name__ == '__main__':
    app.run()
