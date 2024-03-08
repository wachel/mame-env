import asyncio
import socket
import struct
from typing import Dict, List, Tuple, Union
from BaseType import IOPort, Address
import threading
from queue import Queue

fmt_char = {'u8': 'B','u16':'H','u32':'I','s8': 'b','s16':'h','s32':'i'}

class Client():
    def __init__(self, client_socket:socket.socket):
        self.client_socket = client_socket
        self.data:Dict[str,int] = {}
        self.msg_queue:Queue[Tuple[str, bytes]] = Queue()
        self.thread = threading.Thread(target=self._recive_buffer_thread)
        self.thread.start()

    def send_buffer(self, msgID:str, content:bytes):
        assert(len(msgID)==4)
        if isinstance(content, str):
            content = content.encode()
        self.client_socket.send(struct.pack(f'4sI{len(content)}s', (msgID).encode(), len(content), content))

    def send_memory_address(self, addresses:Dict[str, Address]):
        self.addresses = addresses
        mem_address_buff = '|'.join([f'{name},{addr.address},{addr.type}' for name, addr in addresses.items()])
        self.send_buffer('ADDR', mem_address_buff)
        self.unpack_format = '<' + ''.join([fmt_char[addr.type] for name,addr in addresses.items()])

    async def wait_recive_data(self):
        while True:
            await asyncio.sleep(0)
            if not self.msg_queue.empty():
                msgid, content = self.msg_queue.get()
                if msgid == 'DATA':
                    unpacked_data = struct.unpack(self.unpack_format, content)
                    for k,value in zip(self.addresses.keys(), unpacked_data):
                        self.data[k] = value
                    return
                else:
                    print(f'unknown msg {msgid}')

    def _recive_buffer_thread(self):
        buffer = bytes()
        while True:
            buffer += self.client_socket.recv(1024)
            while len(buffer) >= 8:
                msgid,size = struct.unpack("4sI", buffer[0:8]) #msgid and length
                if len(buffer) >= 8 + size:
                    content = buffer[8:8+size]
                    buffer = buffer[8+size:]
                    self.msg_queue.put((msgid.decode(), content))
                else:
                    break

    def send_actions(self, actions:List[IOPort]):
        action_buff = '|'.join([f'{act.tag}+{act.mask}' for act in actions])
        self.send_buffer('ACTS', action_buff)
    
    def send_lua_string(self, lua_string):
        self.send_buffer('ExLS', lua_string)

    def send_write_memory(self, addr_fmt_val_list:List[Tuple[str,str,int]]):
        buff = '|'.join([f'{address}+{fmt}+{value}' for address,fmt,value in addr_fmt_val_list])
        self.send_buffer('WMem', buff)

