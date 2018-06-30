import http
import functools

import mongomock
import bson.json_util
import flask
import flask_pymongo


# TODO: Make this use models.py eventually. Right now we do not need a defined schema as it is much faster to iterate.
def crud(app: flask.Flask, mongo: flask_pymongo.PyMongo or mongomock.MongoClient, name: str):
    base = '/{}'.format(name)
    base_id = '{}/<_id>'.format(base)

    def set_name(func):
        func.__name__ = '{}_{}'.format(name, func.__name__)
        return func

    def get_collection(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs, collection=mongo.db[name])
        return wrapper

    def process_id(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['_id'] = bson.ObjectId(kwargs['_id'])
            return func(*args, **kwargs)
        return wrapper

    @app.route(base, methods=['GET'])
    @set_name
    @get_collection
    def get_all(collection):
        return bson.json_util.dumps(collection.find())

    @app.route(base_id, methods=['GET'])
    @set_name
    @get_collection
    @process_id
    def get_one(collection, _id):
        return bson.json_util.dumps(collection.find_one(_id))

    @app.route(base, methods=['POST'])
    @set_name
    @get_collection
    def create(collection):
        collection.insert(flask.request.json)
        return 'created', http.HTTPStatus.CREATED

    @app.route(base_id, methods=['PUT'])
    @set_name
    @get_collection
    @process_id
    def update(collection, _id):
        instance = collection.find_one({'_id': _id})
        instance = {**instance, **flask.request.json}  # flask.request.json overwrites instance
        _id = instance['_id']
        del instance['_id']
        collection.replace_one({'_id': _id}, instance)
        return 'updated'

    @app.route(base_id, methods=['DELETE'])
    @set_name
    @get_collection
    @process_id
    def delete(collection, _id):
        collection.remove(_id)
        return 'deleted'
