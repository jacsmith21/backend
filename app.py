from flask import Flask
from flask import request
from flask import jsonify
from flask_pymongo import PyMongo

import crud
import parser

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'curriculummapping'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/curriculummapping'

mongo = PyMongo(app)

crud.crud(app, mongo, 'courses')
crud.crud(app, mongo, 'benchmarks')


@app.route('/', methods=['POST'])
def hello_world():
    res = parser.parse(request.json['expression']).to_dict()
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
