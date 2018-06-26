from flask import Flask
from flask import request
from flask import jsonify

import parser

app = Flask(__name__)


@app.route('/', methods=['POST'])
def hello_world():
    print(request.json)
    res = parser.parse(request.json['expression']).to_dict()
    print(res)
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
