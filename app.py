import bson
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
import utils

app = Flask(__name__)

app.config['MONGO_DBNAME'] = config.db.name
app.config['MONGO_URI'] = config.db.uri

flask_cors.CORS(app)

mongo = PyMongo(app)

crud.crud(app, mongo, 'courses')
crud.crud(app, mongo, 'benchmarks')


@app.route('/export/<_id>')
def export(_id):
    collection = mongo.db.courses
    _id = bson.ObjectId(_id)
    course = collection.find_one(_id)
    with utils.export(course) as path:
        return flask.send_file(path, mimetype='application/vnd.ms-excel', as_attachment=True)


@app.route('/login', methods=['POST'])
def login():
    username = flask.request.json.get('username')
    password = flask.request.json.get('password')

    try:
        user = mongo.db.users.find_one({'username': username})
    except pymongo.errors.ServerSelectionTimeoutError:
        return 'Unable to connect to the database.', http.HTTPStatus.INTERNAL_SERVER_ERROR

    if not user or not security.check_password_hash(user['password'], password):
        return 'Username or password is incorrect.', http.HTTPStatus.BAD_REQUEST

    token = jwt.encode(
        {
            'sub': user['username'],
            'iat': int(time.time()),
            'exp': int(time.time()) + 60*60  # 60 minutes
        },
        config.secret_key
    )

    return flask.jsonify(token.decode('UTF-8'))


@app.route('/register', methods=['POST'])
def register():
    json = flask.request.json
    username, password, code = json.get('username'), json.get('password'), json.get('code')

    if code != config.code:
        return flask.jsonify('Invalid code.'), http.HTTPStatus.BAD_REQUEST

    if not password or not json.get('initials'):
        return flask.jsonify('Bad data.'), http.HTTPStatus.BAD_REQUEST

    user = mongo.db.users.find_one({'username': username})
    if user is not None:
        return flask.jsonify('Username already exists.'), http.HTTPStatus.BAD_REQUEST

    json['password'] = security.generate_password_hash(password, method='sha256')
    mongo.db.users.insert_one(flask.request.json)

    return 'OK'


@app.route('/', methods=['GET'])
def root():
    return 'Welcome to Jacob\'s application. This is the API!'


@app.route('/parse', methods=['GET'])
@utils.authenticate(mongo)
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
            'number': course['number'],
            'prereqTree': to_dict(course.get('prerequisites', '')),
            'coreqTree': to_dict(course.get('corequisites', ''))
        })

    return flask.jsonify(parsed)


if __name__ == '__main__':
    app.run()
