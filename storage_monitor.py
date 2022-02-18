import psutil

from datatype import DataType, scaled_unit


def storage_info(unit: DataType) -> dict:
    storage = psutil.disk_usage('/')
    storage_dict = {
        'total': storage[0],
        'percent': storage[3],
        'used': storage[1],
        'free': storage[2],
    }
    for memory in storage_dict:
        if memory != 'percent':
            storage_dict[memory] = scaled_unit(unit, storage_dict[memory])
    return storage_dict
