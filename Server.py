import struct
from typing import Dict, List
from Connect import Connect
from BaseType import Action, Address
import time

class Server():
    def __init__(self, host='127.0.0.1', port=12000, addresses:Dict[str,Address]={}):
        self.connect = Connect(host, port, connect_callback=self.on_recv_connet)
        self.addresses = addresses
        self.mem_datas:List[Dict[str,int]] = []
        self.client_num = 0
        self.received_num = 0

        self.addresses_fmt = '<'
        fmt_char = {'u8':'B', 'u16':'H', 'u32':'I', 's8':'b', 's16':'h', 's32':'i'}
        for key, address in self.addresses.items():
            self.addresses_fmt += fmt_char[address.type]
    
    def on_recv_connet(self, sid):
        self.client_num += 1
        self.mem_datas.append({})
        s = '|'.join([f'{name},{addr.address},{addr.type}' for name, addr in self.addresses.items()])
        self.connect.send(sid, 'ADDR', s.encode())

    def _on_recv_data(self, sid, msgid, content):
        if msgid == "MDAT":
            data = {}
            unpacked_data = struct.unpack(self.addresses_fmt, content)
            for k,value in zip(self.addresses.keys(), unpacked_data):
                data[k] = value
            self.mem_datas[sid] = data
            self.received_num += 1

    def read_mem_data(self):
        self.received_num = 0
        while self.received_num < self.client_num:
            self.connect.pick_all_data(self._on_recv_data)
        return self.mem_datas
    
    def send_actions(self, all_actions:List[List[Action]]):
        for i in range(self.client_num):
            actions = all_actions[i]
            buff = '|'.join([f'{act.port}+{act.field}' for act in actions])
            self.connect.send(i, 'ACTN', buff.encode())
