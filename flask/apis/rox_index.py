import datetime
from base.searchsets import *


# ROX Index Patient's ID api
def rox_index_calc_with_patient_id(id, table, dataAliveTime):
    # default_time變數是為模型訓練用, 這裡不需要這種東西
    default_time = datetime.datetime.now()

    # prepare all the data to search
    # put all the resource we need in data
    data = dict()
    for key in table:
        data[key] = dict()
        data[key] = get_resources(
            id, table[key], default_time, dataAliveTime=dataAliveTime)

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
    result_dict['predict_value'] = rox_model_result(result_dict)
    return result_dict


def rox_index_calc_with_score(dict):
    """
        dict: {
            "respiratory rate": {
                "date": (YYYY-MM-DD)T(HH:MM),
                "value": 25
            },
            "fio2": {
                "date": (YYYY-MM-DD)T(HH:MM),
                "value": 60
            },
            "spo2": {
                "date": (YYYY-MM-DD)T(HH:MM),
                "value": 25
            }
        }
    """
    result_dict = dict
    result_dict['predict_value'] = rox_model_result(result_dict)
    return result_dict


def rox_model_result(dict):
    # return integer or double
    return '%.2f' % (int(dict['spo2']['value']) / int(dict['fio2']['value']) / int(dict['respiratory rate']['value']) * 100)


def estimate_fio2(fio2_resources):
    if fio2_resources.valueQuantity.unit in 'liters/min':
        return fio2_resources.valueQuantity.value * 4 + 21
    return fio2_resources.valueQuantity.value
