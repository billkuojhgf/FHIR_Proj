import csv
import json

import datetime
from fhirpy import SyncFHIRClient
from fhirpy.base.exceptions import ResourceNotFound
from fhirpy.base.searchset import *
from dateutil.relativedelta import relativedelta

import joblib

CLIENT = SyncFHIRClient('http://192.168.0.125:5555/fhir')
# TODO: Do it with ASync
TIME_FORMAT = '%Y-%m-%d'


def diabetes(id, table, default_time=None):
    # default_time變數是為模型訓練用(type=date or datetime)，數值放入patient得病的時間，None表示使用現在時間
    x = list()
    if default_time == None:
        default_time = datetime.datetime.now()

    # put all the resource we need in data
    data = dict()
    for key in table:
        # data[key] = {'resource': resource, 'is_in_component': type(boolean), 'type': 'laboratory' or 'diagnosis'}
        data[key] = dict()
        # Return dict of resources
        data[key] = get_resources(id, table[key], default_time)
    data['age'] = get_age(id, default_time)

    # Put all the values into temp and get ready to predict
    temp = [6, get_value(data['glucose']), get_value(data['diastolic blood pressure']), 35, get_value(
        data['insulin']), bmi(data['height']['resource'], data['weight']['resource']), 0.627, data['age']]
    loaded_model = joblib.load('finalized_model.sav')
    x.append(temp)
    result_proba = loaded_model.predict_proba(x)

    result_dict = dict()
    # result_proba = [no's probability, yes's probability]
    result_dict['risk_proba'] = result_proba[:, 1][0]
    for key in data:
        result_dict[key] = dict()
        result_dict[key]['date'] = get_resource_datetime(data[key])
        result_dict[key]['value'] = get_value(data[key])
    return json.dumps(result_dict)


def get_resources(id, table, default_time):
    if table['type'].lower() == 'observation':
        # How to differentiate the code that user give is code or component-code?
        resources = CLIENT.resources('Observation')
        search = resources.search(subject=id, date__ge=(default_time - relativedelta(
            years=5)).strftime('%Y-%m-%d'), code=table['code']).sort('-date').limit(1)
        resources = search.fetch()
        is_in_component = False
        if len(resources) == 0:
            resources = CLIENT.resources('Observation')
            search = resources.search(subject=id, date__ge=(default_time - relativedelta(
                years=5)).strftime('%Y-%m-%d'), component_code=table['code']).sort('-date').limit(1)
            resources = search.fetch()
            is_in_component = True
            if len(resources) == 0:
                raise ResourceNotFound(
                    'Could not find the resources, no enough data for the patient')
        for resource in resources:
            return {'resource': resource, 'is_in_component': is_in_component, 'component-code': table['code'] if is_in_component else '', 'type': 'laboratory'}
    elif table['type'].lower() == 'condition':
        resources = CLIENT.resources('Condition')
        search = resources.search(
            subject=id, code=table['code']).sort('-date').limit(1)
        resources = search.fetch()
        if len(resources) == 0:
            return {'resource': None, 'is_in_component': False, 'type': 'diagnosis'}
        else:
            for resource in resources:
                return {'resource': resource, 'is_in_component': False, 'type': 'diagnosis'}
    else:
        raise Exception('unknown type of data')


def get_age(id, default_time):
    # Getting patient data from server
    resources = CLIENT.resources('Patient')
    resources = resources.search(_id=id).limit(1)
    patient = resources.get()
    patient_birthdate = datetime.datetime.strptime(
        patient.birthDate, '%Y-%m-%d')
    # If we need the data that is 1 year before or so, return the real age at the time
    age = default_time - patient_birthdate
    return int(age.days/365)


def get_value(dictionary):
    if type(dictionary) is not dict:
        return dictionary
    # dictionary = {'resource': resource, 'is_in_component': type(boolean), 'component-code': type(str), 'type': 'laboratory' or 'diagnosis'}
    if dictionary['type'] == 'diagnosis':
        return False if dictionary['resource'] is None else True
    elif dictionary['type'] == 'laboratory':
        # Two situation: one is to get the value of resource, the other is to get the value of resource.component
        if dictionary['is_in_component']:
            for component in dictionary['resource'].component:
                for coding in component.code.coding:
                    if coding.code == dictionary['component-code']:
                        return component.valueQuantity.value
        else:
            try:
                return dictionary['resource'].valueQuantity.value
            except KeyError:
                return dictionary['resource'].valueString


def get_resource_datetime(dictionary):
    # dictionary = {'resource': resource, 'is_in_component': type(boolean), 'component-code': type(str), 'type': 'laboratory' or 'diagnosis'}
    if type(dictionary) is not dict:
        return 'null'
    if dictionary['type'] == 'diagnosis':
        return dictionary['resource'].recordedDate[:10]
    elif dictionary['type'] == 'laboratory':
        try:
            return dictionary['resource'].effectiveDateTime[:10]
        except KeyError:
            try:
                return dictionary['resource'].effectivePeriod.start[:10]
            except KeyError:
                return 'null'


def bmi(height_resource, weight_resource):
    # weight(unit: kilogram)/ height(unit: meter)/ height(unit: meter)
    weight = {
        'kg': weight_resource.valueQuantity.value,
        'g': weight_resource.valueQuantity.value / 1000,
        'pound': weight_resource.valueQuantity.value * 0.45359237
    }.get(weight_resource.valueQuantity.unit, 0)
    height = {
        'cm': height_resource.valueQuantity.value / 100,
        'inch': height_resource.valueQuantity.value * 0.0254,
        'm': height_resource.valueQuantity.value
    }.get(height_resource.valueQuantity.unit, 0)

    return weight / height / height


if __name__ == '__main__':
    id = input('id: ')
    table = {}
    table_position = "./table/table_example_V2.csv"
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

    print(diabetes(id, table['diabetes']))
