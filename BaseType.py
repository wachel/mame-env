from enum import Enum
from typing import Dict

class DataType(Enum):
    u8 = 'u8'
    s8 = 's8'
    u16 = 'u16'
    s16 = 's16'

class Address:
    def __init__(self, address = 0x0, type:DataType=DataType.u8):
        self.address = address
        self.type = type

class Action(object):
    def __init__(self, port, field):
        self.port = port
        self.field = field
