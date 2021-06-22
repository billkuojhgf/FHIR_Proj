import datetime
from fhirpy import SyncFHIRClient
from fhirpy.base.searchset import *
from fhirpy.base.exceptions import ResourceNotFound
from dateutil.relativedelta import relativedelta

from base.exceptions import *

CLIENT = SyncFHIRClient('http://192.168.0.125:5555/fhir')

def get_resources(id, table, default_time):
    if table['type'].lower() == 'observation':
        # How to differentiate the code that user give is code or component-code?
        resources = CLIENT.resources('Observation')
        try:
            data = resources.search(subject=id, date__ge=(default_time - relativedelta(
                years=5)).strftime('%Y-%m-%d'), code=table['code']).sort('-date').limit(1)
            resource = data.get()
            is_in_component = False
        except ResourceNotFound:
            try:
                data = resources.search(subject=id, date__ge=(default_time - relativedelta(
                    years=5)).strftime('%Y-%m-%d'), component_code=table['code']).sort('-date').limit(1)
                resource = data.get()
                is_in_component = True
            except ResourceNotFound:
                raise ResourceNotFound(
                    "Could not find the resources {}, no enough data for the patient".format(table['feature']))
        return {'resource': resource, 'is_in_component': is_in_component, 'component-code': table['code'] if is_in_component else '', 'type': 'laboratory'}

    elif table['type'].lower() == 'condition':
        resources = CLIENT.resources('Condition')
        data = resources.search(
            subject=id, code=table['code']).sort('-date').limit(1)
        try:
            resource = data.get()
        except ResourceNotFound:
            return {'resource': None, 'is_in_component': False, 'type': 'diagnosis'}
        else:
            return {'resource': resource, 'is_in_component': False, 'type': 'diagnosis'}

    else:
        raise TypeUnknown('unknown type of data: {}'.format(table['feature']))


def get_age(id, default_time):
    # Getting patient data from server
    resources = CLIENT.resources('Patient')
    resources = resources.search(_id=id).limit(1)
    patient = resources.get()
    patient_birthdate = datetime.datetime.strptime(
        patient.birthDate, '%Y-%m-%d')
    # If we need the data that is 1 year before or so, return the real age at the time
    age = default_time - patient_birthdate
    return int(age.days / 365)


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
