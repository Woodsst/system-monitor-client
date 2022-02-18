import psutil

from datatype import DataType, scaled_unit


def memory_info(unit: DataType) -> dict:
    mem = psutil.virtual_memory()
    memory_dict = {
        'total': mem[0],
        'available': mem[1],
        'percent': mem[2],
        'used': mem[3],
        'free': mem[4],
        'active': mem[5],
        'inactive': mem[6],
        'buffers': mem[7],
        'cached': mem[8],
        'shared': mem[9],
        'slab': mem[10],
    }
    for memory in memory_dict:
        if memory != 'percent':
            memory_dict[memory] = scaled_unit(unit, memory_dict[memory])
    return memory_dict
