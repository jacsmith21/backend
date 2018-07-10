import http

import bson.json_util
import unittest

import jsonpatch
import mongomock
from flask import Flask

import crud
import utils


class TestCrud(unittest.TestCase):
    # noinspection PyTypeChecker
    def setUp(self):
        app = Flask(__name__)

        mongo = mongomock.MongoClient()
        crud.crud(app, mongo, 'tests')

        self.app = app.test_client()

        self.objects = [dict(foo='bar'), dict(foo='rab')]
        self.objects = [dict(current=obj.copy(), base=obj.copy(), patch=[]) for obj in self.objects]

        obj = self.objects[0]['current'].copy()
        obj['bat'] = 'br'
        obj['foo'] = 'br'
        patch = jsonpatch.make_patch(self.objects[0]['current'], obj).patch
        patch[0]['time'] = utils.unix_time(utils.date_to_datetime('2016-01-01'))
        patch[1]['time'] = utils.unix_time(utils.date_to_datetime('2017-01-01'))
        self.objects[0]['patch'] = patch
        self.objects[0]['current'] = obj

        for obj in self.objects:
            obj['_id'] = mongo.db.tests.insert(obj)

    def test_get_all(self):
        res = self.app.get('/tests')
        data = bson.json_util.loads(res.data)
        assert isinstance(data, list)
        assert len(data) == len(self.objects)
        assert res.status_code == 200

    def test_get_one(self):
        res = self.app.get('/tests/{}'.format(self.objects[0]['_id']))
        data = bson.json_util.loads(res.data)
        assert isinstance(data, dict)
        assert data['foo'] == 'br'
        assert res.status_code == http.HTTPStatus.OK

    def test_get_one_with_date(self):
        res = self.app.get('/tests/{}?date={}'.format(self.objects[0]['_id'], '2016-05-05'))
        data = bson.json_util.loads(res.data)
        assert isinstance(data, dict)
        assert data == {'_id': str(self.objects[0]['_id']), 'foo': 'bar', 'bat': 'br'}

    def test_create(self):
        res = self.app.post('/tests', data=bson.json_util.dumps(dict(foo='oof')), content_type='application/json')
        assert res.status_code == http.HTTPStatus.CREATED

    def test_patch(self):
        new_obj = self.objects[0].copy()
        new_obj['foo'] = 'bbar'
        patch = jsonpatch.make_patch(self.objects[0], new_obj)

        res = self.app.patch(
            '/tests/{}'.format(self.objects[0]['_id']),
            data=bson.json_util.dumps(patch),
            content_type='application/json')

        assert res.status_code == http.HTTPStatus.OK

    def test_delete(self):
        res = self.app.delete('/tests/{}'.format(self.objects[0]['_id']))
        assert res.status_code == http.HTTPStatus.OK
