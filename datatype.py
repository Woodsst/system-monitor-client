import enum


class DataType(enum.Enum):
    Terabyte = 'TB'
    Gigabyte = 'GB'
    Megabyte = 'MB'
    Kilobyte = 'KB'
    Byte = 'B'


UNIT_SCALE = {
        DataType.Terabyte: 1024 ** 4,
        DataType.Gigabyte: 1024 ** 3,
        DataType.Megabyte: 1024 ** 2,
        DataType.Kilobyte: 1024,
        DataType.Byte: 1,
    }


def scaled_unit(unit: DataType, value) -> float:
    scale = UNIT_SCALE.get(unit)
    return value // scale
