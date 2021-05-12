import json
from fhirpy import SyncFHIRClient
import datetime
from fhirpy.base.searchset import *
import pytz
import joblib

client = SyncFHIRClient('http://192.168.0.125:5555/fhir')


def main(id, default_time=None):
    x = list()
    if default_time == None:
        temp = [6, get_glucose(id), get_blood_pressure(
            id), 35, get_insulin(id), get_bmi(id), 0.627, get_age(id)]
    else:
        temp = [6, get_glucose(id, default_time), get_blood_pressure(
            id, default_time), 35, get_insulin(id, default_time), get_bmi(id, default_time), 0.627, get_age(id, default_time)]
    loaded_model = joblib.load('finalized_model.sav')
    x.append(temp)
    result = loaded_model.predict_proba(x)
    # result = [no's probability, yes's probability]
    print(result, x)


def get_glucose(id, default_time=datetime.datetime.utcnow().year):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code': '72-314'})).sort('-date')
    # observation.code:text = "Glucose"
    observations = resources.fetch()
    for observation in observations:
        time = datetime.datetime.strptime(
            observation.effectedDatetime, '%Y-%m-%d')
        if time.year < datetime.datetime.utcnow().year:
            return observation.valueQuantity.value


def get_blood_pressure(id, default_time=None):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'component-code': 'http://loinc.org|8462-4'})).sort('-date')
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


def get_insulin(id, default_time=None):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code:text': 'Insulin'})).sort('-date')
    # observation.code = "72-496"
    observations = resources.fetch()
    # why using fetch? Because observations will not only have one resource
    # maybe we can use the function sort() and first() to fetch the first resource
    for observation in observations:
        return observation.valueQuantity.value


def get_bmi(id, default_time=None):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code': 'http://loinc.org|29463-7'})).sort('-date')
    weight_observation = resources.fetch()
    for weights in weight_observation:
        weight = {
            'kg': weights.valueQuantity.value,
            'pound': weights.valueQuantity.value * 0.45359237
        }.get(weights.valueQuantity.unit, 0)

    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code': 'http://loinc.org|8302-2'})).sort('-date')
    height_observation = resources.fetch()
    # TODO: Consider inch and pound
    for heights in height_observation:
        height = {
            'cm': heights.valueQuantity.value / 100,
            'inch': heights.valueQuantity.value * 0.0254,
            'm': heights.valueQuantity.value
        }.get(heights.valueQuantity.unit, 0)

    try:
        return weight / height / height


def get_age(id, default_time=None):
    # Getting patient data from server
    resources = client.resources('Patient')
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
    main('test-03121002')
