import http
import functools
import time

import jsonpatch
import mongomock
import bson.json_util
import flask
import flask_pymongo

import utils


def crud(app: flask.Flask, mongo: flask_pymongo.PyMongo or mongomock.MongoClient, name: str):
    base = '/{}'.format(name)
    base_id = '{}/<_id>'.format(base)

    def set_name(func):
        """Sets the name because each function name must be unique."""
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
    @utils.authenticate(mongo)
    @set_name
    @get_collection
    @postprocess
    def get_all(collection):
        return collection.find()

    @app.route('{}/history'.format(base_id), methods=['GET'])
    @utils.authenticate(mongo)
    @set_name
    @get_collection
    @process_id
    def get_history(collection, _id):
        instance = collection.find_one(_id)
        return bson.json_util.dumps(instance['patch'])

    @app.route(base_id, methods=['GET'])
    @utils.authenticate(mongo)
    @set_name
    @get_collection
    @process_id
    @postprocess
    def get_one(collection, _id):
        t = flask.request.args.get('time')
        if t is None:
            return collection.find_one(_id)
        else:
            t = int(t)

            instance = collection.find_one(_id)
            history = instance['patch']

            i = 0
            for operation in history:
                if t < operation['time']:
                    break
                i += 1
            json_patch = jsonpatch.JsonPatch(history[:i])
            return {
                '_id': instance['_id'],
                'current': json_patch.apply(instance['base'])
            }

    @app.route(base, methods=['POST'])
    @utils.authenticate(mongo)
    @set_name
    @get_collection
    def create(collection):
        result = collection.insert_one(utils.format_json(flask.request.json))
        return str(result.inserted_id), http.HTTPStatus.CREATED

    @app.route(base_id, methods=['PATCH'])
    @utils.authenticate(mongo)
    @set_name
    @get_collection
    @process_id
    def patch(collection, _id, user):
        instance = collection.find_one({'_id': _id})
        operations = flask.request.json
        _type = flask.request.args.get('type')
        timestamp = time.time()
        operations = [{**operation, 'time': timestamp, 'type': _type, 'initials': user['initials']} for operation in operations]
        instance['patch'].extend(operations)

        json_patch = jsonpatch.JsonPatch(operations)
        instance['current'] = json_patch.apply(instance['current'])

        collection.replace_one({'_id': _id}, instance)
        return 'patched'

    @app.route(base_id, methods=['DELETE'])
    @utils.authenticate(mongo)
    @set_name
    @get_collection
    @process_id
    def delete(collection, _id):
        collection.delete_one({'_id': _id})
        return 'deleted'
