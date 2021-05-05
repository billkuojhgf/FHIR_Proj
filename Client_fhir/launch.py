import json
from fhirpy import SyncFHIRClient
import datetime
from fhirpy.base.searchset import *
import pytz
import joblib

client = SyncFHIRClient('http://192.168.0.125:5555/fhir')


def main(id):
    x = [6, get_glucose(id), get_blood_pressure(
        id), 35, get_insulin(id), get_bmi(id), 0.627, get_age(id)]
    loaded_model = joblib.load('finalized_model.sav')
    result = loaded_model.predict_proba(x)
    print(result, x)


def get_glucose(id):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code': 'Glucose(AC)'}))
    observations = resources.fetch()
    for observation in observations:
        return observation.valueQuantity.value


def get_blood_pressure(id):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'component-code': 'http://loinc.org|8462-4'}))
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


def get_insulin(id):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code': 'Insulin'}))
    observations = resources.fetch()
    # why using fetch? Because observations will not only have one resource
    # maybe we can use the function sort() and first() to fetch the first resource
    for observation in observations:
        return observation.valueQuantity.value


def get_bmi(id):
    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code': 'http://loinc.org|29463-7'}))
    weight_observation = resources.fetch()
    for weights in weight_observation:
        weight = weights.valueQuantity.value

    resources = client.resources('Observation')
    resources = resources.search(
        Raw(**{'subject': id, 'code': 'http://loinc.org|8302-2'}))
    height_observation = resources.fetch()
    for heights in height_observation:
        if heights.valueQuantity.unit == 'cm':
            height = heights.valueQuantity.value / 100
        else:
            height = heights.valueQuantity.value
    return weight/height/height


def get_age(id):
    # Getting patient data from server
    resources = client.resources('Patient')
    resources = resources.search(_id=id).limit(1)
    patient = resources.get()
    #age = time.now - patient.birthdate
    now_time = datetime.datetime.utcnow()
    patient_birthdate = datetime.datetime.strptime(
        patient.birthDate, '%Y-%m-%d')
    age = now_time - patient_birthdate
    return int(age.days/365)


if __name__ == '__main__':
    main('test-03121002')
