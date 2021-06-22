import json

import joblib
import datetime

from base.searchsets import *


def diabetes_predict(id, table, default_time=None):
    # default_time變數是為模型訓練用(type=date or datetime)，數值放入patient得病的時間，None表示使用現在時間
    if default_time == None:
        default_time = datetime.datetime.now()

    # put all the resource we need in data
    data = dict()
    for key in table:
        data[key] = dict()
        data[key] = get_resources(id, table[key], default_time)
    data['age'] = get_age(id, default_time)

    # Put all the values into temp and get ready to predict
    x = list()
    temp = [6, get_value(data['glucose']), get_value(data['diastolic blood pressure']), 35, get_value(
        data['insulin']), bmi(data['height']['resource'], data['weight']['resource']), 0.627, data['age']]
    loaded_model = joblib.load('finalized_model.sav')
    x.append(temp)
    result_proba = loaded_model.predict_proba(x)

    # Put all the result and datas into result_dict and return as json format
    result_dict = dict()
    # result_proba = [no's probability, yes's probability]
    result_dict['predict_value'] = result_proba[:, 1][0]
    for key in data:
        result_dict[key] = dict()
        result_dict[key]['date'] = get_resource_datetime(data[key])
        result_dict[key]['value'] = get_value(data[key])
    return json.dumps(result_dict)
