import http
import functools

import jsonpatch as jsonpatch
import mongomock
import bson.json_util
import flask
import flask_pymongo

import utils


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

    def postprocess(func):
        def process_item(item):
            return {'_id': str(item['_id']), **item['current']}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            unprocessed = func(*args, **kwargs)
            if isinstance(unprocessed, dict):
                return bson.json_util.dumps(process_item(unprocessed))
            else:
                return bson.json_util.dumps([process_item(item) for item in unprocessed])

        return wrapper

    @app.route(base, methods=['GET'])
    @set_name
    @get_collection
    @postprocess
    def get_all(collection):
        return collection.find()

    @app.route(base_id, methods=['GET'])
    @set_name
    @get_collection
    @process_id
    @postprocess
    def get_one(collection, _id):
        return collection.find_one(_id)

    @app.route(base, methods=['POST'])
    @set_name
    @get_collection
    def create(collection):
        collection.insert_one(utils.format_json(flask.request.json))
        return 'created', http.HTTPStatus.CREATED

    @app.route(base_id, methods=['PATCH'])
    @set_name
    @get_collection
    @process_id
    def patch(collection, _id):
        instance = collection.find_one({'_id': _id})
        instance['patch'].extend(flask.request.json)

        json_patch = jsonpatch.JsonPatch(flask.request.json)
        instance['current'] = json_patch.apply(instance['current'])

        collection.replace_one({'_id': _id}, instance)
        return 'patched'

    @app.route(base_id, methods=['DELETE'])
    @set_name
    @get_collection
    @process_id
    def delete(collection, _id):
        collection.delete_one({'_id': _id})
        return 'deleted'
