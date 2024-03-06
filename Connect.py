import socket
import struct
from typing import List
import time
from Console import ConsoleProcess

class SocketConnect:
    def __init__(self, client_socket:socket.socket):
        self.client_socket = client_socket
        self.buffer = bytes()

    def send(self, msgID:str, content:bytes):
        assert(len(msgID)==4)
        if isinstance(content, str):
            content = content.encode()
        self.client_socket.send(struct.pack(f'4sI{len(content)}s', (msgID).encode(), len(content), content))
    
    def recive(self):
        result = []
        self.buffer += self.client_socket.recv(1024)
        if len(self.buffer) >= 8:
            msgid,size = struct.unpack("4sI", self.buffer[0:8]) #msgid and length
            msgid = msgid.decode()
            if len(self.buffer) >= 8 + size:
                content = self.buffer[8:8+size]
                self.buffer = self.buffer[8+size:]
                result.append((msgid, content))
        return result

class SocketServer:
    def __init__(self,  host='127.0.0.1', port=12001):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)
    
    def accept_connects(self, total_num)->List[SocketConnect]:
        connects = []
        for i in range(total_num):
            client_socket, client_address = self.socket.accept()
            connects.append(SocketConnect(client_socket))
        return connects
    
    # def run(self, rom_dir, game_id, mame_bin_path, addresses, client_num = 1):
    #     consoles = []
    #     for i in range(client_num):
    #         consoles.append(ConsoleProcess('roms', 'kof98', mame_bin_path=mame_bin_path, port=server.port, render=i==0))

    #     client_sockets = server.accept_connects(client_num)

    #     mem_address_buff = '|'.join([f'{name},{addr.address},{addr.type}' for name, addr in addresses.items()])
    #     for client in client_sockets:
    #         client.send('ADDR', mem_address_buff)

    #     frame = 0
    #     while True:
    #         frame += 1

    #         client_sockets2 = client_sockets.copy()
    #         while len(client_sockets2) > 0:
    #             for i, x in reversed(list(enumerate(client_sockets2))):
    #                 msgs = client.recive()
    #                 for msgid, content in msgs:
    #                     if msgid == 'DATA':
    #                         actions = []
    #                         if (frame//5)%2==0:
    #                             actions.extend(kof_actions['a'])
    #                         action_buff = '|'.join([f'{act.port}+{act.field}' for act in actions])
    #                         client.send('ACTN', action_buff)
    #                         del client_sockets2[i]


if __name__ == '__main__':
    server = SocketServer()
    server.accept_connects(2)
    print('ok')