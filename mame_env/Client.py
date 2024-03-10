import asyncio
import socket
import struct
from typing import Dict, List, Tuple, Union
from .BaseType import IOPort, Address

fmt_char = {'u8': 'B','u16':'H','u32':'I','s8': 'b','s16':'h','s32':'i'}

class AsyncClient():
    def __init__(self, index, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.index = index
        self.data:Dict[str,int] = {}
        self.wait_data = 0

    def send_buffer(self, msgID:str, content:bytes):
        assert(len(msgID)==4)
        if isinstance(content, str):
            content = content.encode()
        self.writer.write(struct.pack(f'4sI{len(content)}s', (msgID).encode(), len(content), content))

    def send_memory_address(self, addresses:Dict[str, Address]):
        self.addresses = addresses
        mem_address_buff = '|'.join([f'{name},{addr.address},{addr.type}' for name, addr in addresses.items()])
        self.send_buffer('ADDR', mem_address_buff)
        self.unpack_format = '<' + ''.join([fmt_char[addr.type] for name,addr in addresses.items()])

    async def reader_read_length(self, length):
        received_data = bytearray()
        while len(received_data) < length:
            data = await self.reader.read(length - len(received_data))
            if not data: #连接断开
                break
            received_data.extend(data)
            if len(received_data) >= length:
                break
        return received_data

    async def read_data(self):
        self.data = {}
        while True:
            buffer = await self.reader_read_length(8)
            msgid,size = struct.unpack("4sI", buffer) #get msgid and length
            msgid = msgid.decode()
            content = await self.reader_read_length(size)
            if msgid == 'DATA':
                unpacked_data = struct.unpack(self.unpack_format, content)
                for k,value in zip(self.addresses.keys(), unpacked_data):
                    self.data[k] = value
                self.wait_data -= 1
                assert self.wait_data == 0, 'perform_actions and read_data must be paired'
                break
            else:
                print(f'unknown msg {msgid}')

    def perform_actions(self, actions:List[IOPort]):
        action_buff = '|'.join([f'{act.tag}+{act.mask}' for act in actions])
        self.send_buffer('ACTS', action_buff)
        self.wait_data += 1
        assert self.wait_data == 1, 'perform_actions and read_data must be paired'
    
    def execute_lua_string(self, lua_string):
        self.send_buffer('ExLS', lua_string)

    def write_memory(self, addr_fmt_val_list:List[Tuple[str,str,int]]):
        buff = '|'.join([f'{address}+{fmt}+{value}' for address,fmt,value in addr_fmt_val_list])
        self.send_buffer('WMem', buff)

    async def wait_frames(self, frame_num):
        for i in range(frame_num):
            await self.perform_actions_and_read_data([])
        
    async def perform_actions_and_read_data(self, actions):
        self.perform_actions(actions)
        return await self.read_data()
    
class SocketClient:
    def __init__(self, index, client_socket:socket.socket):
        self.socket = client_socket
        self.index = index
        self.data:Dict[str,int] = {}
        self.wait_data = 0

    def send_buffer(self, msgID:str, content:bytes):
        assert(len(msgID)==4)
        if isinstance(content, str):
            content = content.encode()
        self.socket.send(struct.pack(f'4sI{len(content)}s', (msgID).encode(), len(content), content))

    def send_memory_address(self, addresses:Dict[str, Address]):
        self.addresses = addresses
        mem_address_buff = '|'.join([f'{name},{addr.address},{addr.type}' for name, addr in addresses.items()])
        self.send_buffer('ADDR', mem_address_buff)
        self.unpack_format = '<' + ''.join([fmt_char[addr.type] for name,addr in addresses.items()])

    def reader_read_length(self, length):
        received_data = bytearray()
        while len(received_data) < length:
            data = self.socket.recv(length - len(received_data))
            if not data: #连接断开
                break
            received_data.extend(data)
            if len(received_data) >= length:
                break
        return received_data

    def read_data(self):
        self.data = {}

        buffer = self.reader_read_length(8)
        msgid,size = struct.unpack("4sI", buffer) #get msgid and length
        msgid = msgid.decode()
        content = self.reader_read_length(size)
        if msgid == 'DATA':
            unpacked_data = struct.unpack(self.unpack_format, content)
            for k,value in zip(self.addresses.keys(), unpacked_data):
                self.data[k] = value
            self.wait_data -= 1
            assert self.wait_data == 0, 'perform_actions and read_data must be paired'
        else:
            print(f'unknown msg {msgid}')

    def perform_actions(self, actions:List[IOPort]):
        action_buff = '|'.join([f'{act.tag}+{act.mask}' for act in actions])
        self.send_buffer('ACTS', action_buff)
        self.wait_data += 1
        assert self.wait_data == 1, 'perform_actions and read_data must be paired'
    
    def execute_lua_string(self, lua_string):
        self.send_buffer('ExLS', lua_string)

    def write_memory(self, addr_fmt_val_list:List[Tuple[str,str,int]]):
        buff = '|'.join([f'{address}+{fmt}+{value}' for address,fmt,value in addr_fmt_val_list])
        self.send_buffer('WMem', buff)
        
    def perform_actions_and_read_data(self, actions):
        self.perform_actions(actions)
        return self.read_data()
    
    def wait_frames(self, frame_num):
        for i in range(frame_num):
            self.perform_actions_and_read_data([])