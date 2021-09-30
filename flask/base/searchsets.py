import datetime
from fhirpy import SyncFHIRClient
from fhirpy.base.searchset import *
from fhirpy.base.exceptions import ResourceNotFound
from dateutil.relativedelta import relativedelta

from base.exceptions import *

CLIENT = SyncFHIRClient('http://localhost:5555/fhir')


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
        if len(resources) == 0:  # 沒有此condition的搜尋結果
            return {'resource': None, 'is_in_component': False, 'type': 'diagnosis'}
        else:
            for resource in resources:
                return {'resource': resource, 'is_in_component': False, 'type': 'diagnosis'}

    else:
        raise Exception('unknown type of data')


def get_age(id, default_time):
    # TODO: 把取得Patient資料的這個流程加入到get_resources中
    # Getting patient data from server
    resources = CLIENT.resources('Patient')
    resources = resources.search(_id=id).limit(1)
    patient = resources.get()
    patient_birthdate = datetime.datetime.strptime(
        patient.birthDate, '%Y-%m-%d')
    # If we need the data that is 1 year before or so, return the real age at the time
    age = default_time - patient_birthdate
    return int(age.days / 365)


def get_resource_value(dictionary):
    # For value that are not a json format
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


def get_resource_datetime(dictionary, default_time):
    # dictionary = {'resource': resource, 'is_in_component': type(boolean), 'component-code': type(str), 'type': 'laboratory' or 'diagnosis'}
    if type(dictionary) is not dict:
        return default_time.strftime("%Y-%m-%d")

    if dictionary['type'] == 'diagnosis':
        try:
            return dictionary['resource'].recordedDate[:10]
        except AttributeError:
            return None
    elif dictionary['type'] == 'laboratory':
        try:
            return dictionary['resource'].effectiveDateTime[:10]
        except KeyError:
            try:
                return dictionary['resource'].effectivePeriod.start[:10]
            except KeyError:
                return None


def bmi(height_resource, weight_resource):
    # weight(unit: kilogram)/ height(unit: meter)/ height(unit: meter)
    weight = {
        'kg': weight_resource.valueQuantity.value,
        'g': weight_resource.valueQuantity.value / 1000,
        '[lb_av]': weight_resource.valueQuantity.value * 0.45359237
    }.get(weight_resource.valueQuantity.unit, 0)
    height = {
        'cm': height_resource.valueQuantity.value / 100,
        '[in_i]': height_resource.valueQuantity.value * 0.0254,
    }.get(height_resource.valueQuantity.unit, 0)

    return weight / height / height
