import datetime
import http
import time

import jwt
from flask import Flask
import flask
from flask_pymongo import PyMongo
import flask_cors
from werkzeug import security

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
crud.crud(app, mongo, 'users')


@app.route('/login', methods=['POST'])
def login():
    username = flask.request.json.get('username')
    password = flask.request.json.get('password')

    user = mongo.db.users.find_one({'username': username})
    if not user or not security.check_password_hash(user['password'], password):
        return 'BAD', http.HTTPStatus.BAD_REQUEST

    token = jwt.encode(
        {
            'sub': user['username'],
            'iat': time.time(),
            'exp': time.time() + 60*60*30  # 30 minutes
        },
        config.secret_key
    )

    return flask.jsonify(token.decode('UTF-8'))


@app.route('/register', methods=['POST'])
def register():
    json = flask.request.get_json()
    username, password = json.get('username'), json.get('password')

    user = mongo.db.users.find_one({'username': username})
    if user:
        return 'BAD', http.HTTPStatus.BAD_REQUEST

    json['password'] = security.generate_password_hash(password, method='sha256')
    mongo.db.users.insert_one(flask.request.json)

    return 'OK'


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
