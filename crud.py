import http

import flask
import flask_pymongo


# TODO: Make this use models.py
def crud(app: flask.Flask, mongo: flask_pymongo.PyMongo, name: str):
    base = '/{}'.format(name)
    base_id = '{}/<_id>'

    @app.route(base, methods=['GET'])
    def read_all():
        collection = getattr(mongo.db, name)
        return flask.jsonify(collection.find())

    @app.route(base_id, methods=['GET'])
    def read_one(_id):
        collection = getattr(mongo.db, name)
        return flask.jsonify(collection.find_one_or_404(_id))

    @app.route(base, methods=['POST'])
    def create():
        collection = getattr(mongo.db, name)
        collection.insert(flask.request.json)
        return 'created', http.HTTPStatus.CREATED

    @app.route(base_id, methods=['PUT'])
    def update(_id):
        collection = getattr(mongo.db, name)
        instance = collection.find_one_or_404(_id)
        instance = {**instance, **flask.request.json}  # json overwrites instance
        collection.save(instance)
        return 'updated'

    @app.route('/{}/', methods=['DELETE'])
    def delete(_id):
        collection = getattr(mongo.db, name)
        collection.remove(_id)
        return 'deleted'
