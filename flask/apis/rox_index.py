import datetime
from base.searchsets import *


def qcsi_rox_index(id, table):
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
        result_dict[key]['value'] = get_value(data[key])
    return result_dict
