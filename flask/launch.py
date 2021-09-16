import csv
import json
from flask import Flask, url_for, redirect, jsonify, request
from flask_cors import CORS
from apis.diabetes import *
from apis.rox_index import *
from base.exceptions import *

app = Flask(__name__)
CORS(app)

# Map the csv into dictionary
table_position = "./table/table_example.csv"
table = {}
with open(table_position, newline='') as table_example:
    rows = csv.DictReader(table_example)
    for row in rows:
        if row['model'] not in table:
            table[row['model']] = {}
        if row['feature'] not in table[row['model']]:
            table[row['model']][row['feature']] = {}

        if row['code_system'] != '':
            code = "{}|{}".format(row['code_system'], row['code'])
        else:
            code = row['code']
        if code == '':
            raise FeatureCodeIsEmpty(row['feature'])
        if 'code' in table[row['model']][row['feature']]:
            # feature裡面已經有code，則覆蓋+新增
            table[row['model']][row['feature']]['code'] = table[row['model']
                                                                ][row['feature']]['code'] + ",{}".format(code)
        else:
            table[row['model']][row['feature']]['code'] = code
        table[row['model']][row['feature']]['type'] = row['type_of_data']
        table[row['model']][row['feature']]['feature'] = row['feature']


@app.route('/', methods=['GET'])
def index():
    name = ""
    if request.values.get('name'):
        name = request.values.get('name')
        return "Hello " + name
    return "Hello, World!<br/><br/>請在網址列的/後面輸入你要搜尋的病患id即可得出結果<br/>Example: <a href=\"/diabetes?id=test-03121002\">http://localhost:5000/diabetes?id=test-03121002</a>"


@app.route('/<api>', methods=['GET'])
def id_with_api(api):
    if api == 'diabetes':
        if request.values.get('id'):
            id = request.values.get('id')
            return jsonify(diabetes_predict(id, table['diabetes'])), 200
    elif api == 'rox' or api == 'qcsi':
        if request.values.get('id'):
            id = request.values.get('id')
            return jsonify(qcsi_rox_index(id, table['rox'])), 200
    return "", 404


if __name__ == '__main__':
    app.debug = True
    app.run()
