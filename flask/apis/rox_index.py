import datetime
from base.searchsets import *


def rox_index(id, table):
    # default_time變數是為模型訓練用, 這裡不需要這種東西
    default_time = datetime.datetime.now()

    # prepare all the data to search
    # put all the resource we need in data
    data = dict()
    for key in table:
        data[key] = dict()
        data[key] = get_resources(id, table[key], default_time)

    # Put all the result and datas into result_dict and return as json format
    result_dict = dict()
    for key in data:
        result_dict[key] = dict()
        result_dict[key]['date'] = get_resource_datetime(
            data[key], default_time)
        result_dict[key]['value'] = get_resource_value(data[key])
    # estimating FiO2 from oxygen flow
    result_dict['fio2']['value'] = estimate_fio2(data['fio2']['resource'])

    # calculate the score of qcsi_covid
    result_dict['predict_value'] = rox_index_result(result_dict)
    return result_dict


def rox_index_result(dict):
    # return integer or double
    return '%.2f' % (dict['spo2']['value'] / dict['fio2']['value'] / dict['respiratory rate']['value'] * 100)


def estimate_fio2(fio2_resources):
    if fio2_resources.valueQuantity.unit in 'liters/min':
        return fio2_resources.valueQuantity.value * 4 + 21
    return fio2_resources.valueQuantity.value
