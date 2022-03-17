import enum


class DataType(enum.Enum):
    TERABYTE = 'TB'
    GIGABYTE = 'GB'
    MEGABYTE = 'MB'
    KILOBYTE = 'KB'
    BYTE = 'B'


UNIT_SCALE = {
        DataType.TERABYTE: 1024 ** 4,
        DataType.GIGABYTE: 1024 ** 3,
        DataType.MEGABYTE: 1024 ** 2,
        DataType.KILOBYTE: 1024,
        DataType.BYTE: 1,
    }


def scaled_unit(unit: DataType, value) -> float:
    scale = UNIT_SCALE.get(unit)
    return value // scale
