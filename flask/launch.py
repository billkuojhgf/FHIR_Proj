import csv
import json
from flask import Flask, url_for, redirect, jsonify
from apis.diabetes import diabetes_predict

app = Flask(__name__)

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
        if 'code' in table[row['model']][row['feature']]:
            # feature裡面已經有code，則覆蓋+新增
            table[row['model']][row['feature']]['code'] = table[row['model']
                                                                ][row['feature']]['code'] + ",{}".format(code)
        else:
            table[row['model']][row['feature']]['code'] = code
        table[row['model']][row['feature']]['type'] = row['type_of_data']


@app.route('/')
def index():
    return "Hello, World!<br/><br/>請在網址列的/後面輸入你要搜尋的病患id即可得出結果<br/>Example: <a href=\"test-03121002\">http://localhost:5000/diabetes/test-03121002</a>"


@app.route('/<id>')
def id(id, default_time=None):
    return redirect(url_for('id_with_api', api='diabetes', id=id))


@app.route('/<api>/<id>')
def id_with_api(api, id):
    if api == 'diabetes':
        return jsonify(json.loads(diabetes_predict(id, table['diabetes'])))


if __name__ == '__main__':
    app.debug = True
    app.run()
