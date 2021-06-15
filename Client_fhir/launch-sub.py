from flask import jsonify
import json
import csv
from fhirpy import SyncFHIRClient
from dateutil.relativedelta import relativedelta
import pandas as pd
import datetime
from fhirpy.base.searchset import *
import pytz
import joblib

CLIENT = SyncFHIRClient('http://192.168.0.125:5555/fhir')


def diabetes(id, table_position="./table/table_example.csv", default_time=None):
    # Main api
    x = list()
    dataframe = pd.read_csv(table_position)
    if default_time == None:
        default_time = datetime.datetime.now()
    temp = [6, get_glucose(id, dataframe, default_time), get_blood_pressure(
        id, dataframe, default_time), 35, get_insulin(id, dataframe, default_time), get_bmi(id, dataframe, default_time), 0.627, get_age(id, default_time)]
    loaded_model = joblib.load('finalized_model.sav')
    x.append(temp)
    result = loaded_model.predict_proba(x)
    # result = [no's probability, yes's probability]
    return json.dumps({'risk_result': result[:, 1][0]})


def get_glucose(id, dataframe, default_time):
    search_raws = dict()
    search_raws['subject'] = id
    code_value = ''
    for raw in dataframe.glucose.values:
        if str(raw) != 'nan':
            if code_value != '':
                code_value += ',' + str(raw)
            else:
                code_value += str(raw)
    search_raws['code'] = code_value

    resources = CLIENT.resources('Observation')
    resources = resources.search(subject=id, code=code_value,
                                 date__eb=(default_time - relativedelta(years=5)).strftime("%Y-%m-%d")).sort('-date')
    observations = resources.fetch()
    for observation in observations:
        return observation.valueQuantity.value


def get_blood_pressure(id, dataframe, default_time):
    search_raws = dict()
    search_raws['subject'] = id
    code_value = ''
    for raw in dataframe.diastolic_blood_pressure.values:
        if str(raw) != 'nan':
            if code_value != '':
                code_value += ',' + str(raw)
            else:
                code_value += str(raw)
    search_raws['component-code'] = code_value

    resources = CLIENT.resources('Observation')
    resources = resources.search(
        Raw(**search_raws)).sort('-date')
    observations = resources.fetch()
    # Get diastolic blood pressure value
    for observation in observations:
        for component in observation.component:
            for coding in component.code.coding:
                if coding.code == '8462-4':
                    try:
                        return component.valueQuantity.value
                    except:
                        continue


def get_insulin(id, dataframe, default_time):
    search_raws = dict()
    search_raws['subject'] = id
    code_value = ''
    for raw in dataframe.insulin.values:
        if str(raw) != 'nan':
            if code_value != '':
                code_value += ',' + str(raw)
            else:
                code_value += str(raw)
    search_raws['code'] = code_value

    resources = CLIENT.resources('Observation')
    resources = resources.search(
        Raw(**search_raws)).sort('-date')
    # observation.code = "72-496"
    observations = resources.fetch()
    # why using fetch? Because observations will not only have one resource
    # maybe we can use the function sort() and first() to fetch the first resource
    for observation in observations:
        return observation.valueQuantity.value


def get_bmi(id, dataframe, default_time):
    search_raws = dict()
    # Weight
    search_raws['subject'] = id
    code_value = ''
    for raw in dataframe.weight.values:
        if str(raw) != 'nan':
            if code_value != '':
                code_value += ',' + str(raw)
            else:
                code_value += str(raw)
    search_raws['code'] = code_value

    resources = CLIENT.resources('Observation')
    resources = resources.search(
        Raw(**search_raws)).sort('-date')
    weight_observation = resources.fetch()
    for weights in weight_observation:
        weight = {
            'kg': weights.valueQuantity.value,
            'pound': weights.valueQuantity.value * 0.45359237
        }.get(weights.valueQuantity.unit, 0)

    # Height
    for raw in dataframe.height.values:
        if str(raw) != 'nan':
            if code_value != '':
                code_value += ',' + str(raw)
            else:
                code_value += str(raw)
    search_raws['code'] = code_value

    resources = CLIENT.resources('Observation')
    resources = resources.search(
        Raw(**search_raws)).sort('-date')
    height_observation = resources.fetch()
    for heights in height_observation:
        height = {
            'cm': heights.valueQuantity.value / 100,
            'inch': heights.valueQuantity.value * 0.0254,
            'm': heights.valueQuantity.value
        }.get(heights.valueQuantity.unit, 0)

    try:
        return weight / height / height
    except:
        return 0


def get_age(id, default_time):
    # Getting patient data from server
    resources = CLIENT.resources('Patient')
    resources = resources.search(_id=id).limit(1)
    patient = resources.get()
    # age = time.now - patient.birthdate
    # TODO: If we need the data that is 1 year before or so,
    #       how to return the real age of one year before?
    now_time = datetime.datetime.utcnow()
    patient_birthdate = datetime.datetime.strptime(
        patient.birthDate, '%Y-%m-%d')
    age = now_time - patient_birthdate
    return int(age.days/365)


if __name__ == '__main__':
    id = input('id: ')
    print(diabetes(id))
