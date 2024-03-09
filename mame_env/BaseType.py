from enum import Enum
from typing import Dict, List

class DataType(Enum):
    u8 = 'u8'
    s8 = 's8'
    u16 = 'u16'
    s16 = 's16'

class Address:
    def __init__(self, address = 0x0, type:DataType=DataType.u8):
        self.address = address
        self.type = type

class IOPort(object):
    def __init__(self, tag, mask):
        self.tag = tag
        self.mask = mask

class StepAction:
    def __init__(self, wait_frames, actions:List[IOPort]):
        self.wait_frames = wait_frames
        self.actions = actions
    