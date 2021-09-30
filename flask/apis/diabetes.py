import joblib
import datetime

from base.searchsets import *


def diabetes_predict(id, table, default_time=None):
    # default_time變數是為模型訓練用(type=date or datetime)，數值放入patient得病的時間，None表示使用現在時間`
    if default_time == None:
        default_time = datetime.datetime.now()

    # put all the resource we need in data
    data = dict()
    for key in table:
        data[key] = dict()
        data[key] = get_resources(id, table[key], default_time)
    data['age'] = get_age(id, default_time)

    # get model result
    result_proba = diabetes_model_result(data)

    # Put all the result and datas into result_dict and return as json format
    result_dict = dict()
    result_dict['predict_value'] = result_proba
    for key in data:
        result_dict[key] = dict()
        result_dict[key]['date'] = get_resource_datetime(
            data[key], default_time)
        result_dict[key]['value'] = get_resource_value(data[key])
    return result_dict


def diabetes_model_result(data):
    # @data comes from two places, one is from diabetes_predict(), the other is from flask(not sure where yet).
    # data allows two kind of value set, one is dictionary(the value returned from get_resources()),
    #   another is value(the value comes from frontend)
    # Put all the values into temp and get ready to predict
    x = list()
    # fixed variable: pregnancies=6, skinthickness=35, diabetespedigreefunction=0.627
    # controlled variable: glucose, diastolic blood pressure, insulin, height, weight, age
    temp = [6, get_resource_value(data['glucose']), get_resource_value(data['diastolic blood pressure']), 35, get_resource_value(
        data['insulin']), bmi(data['height']['resource'], data['weight']['resource']), 0.627, data['age']]
    loaded_model = joblib.load("./models/finalized_model.sav")
    x.append(temp)
    result = loaded_model.predict_proba(x)
    # result = [no's probability, yes's probability]
    # return negative's probability
    return result[:, 1][0]
