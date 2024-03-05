import socket
import struct
from typing import List
import time

class SocketConnect:
    def __init__(self, client_socket:socket.socket):
        self.client_socket = client_socket

    def send(self, msgID:str, content:bytes):
        assert(len(msgID)==4)
        if isinstance(content, str):
            content = content.encode()
        self.client_socket.send(struct.pack(f'4sI{len(content)}s', (msgID).encode(), len(content), content))
    
    def recive(self):
        result = []
        current_buffer = bytes()
        while True:
            current_buffer += self.client_socket.recv(1024)
            if len(current_buffer) >= 8:
                msgid,size = struct.unpack("4sI", current_buffer[0:8]) #msgid and length
                msgid = msgid.decode()
                if len(current_buffer) >= 8 + size:
                    content = current_buffer[8:8+size]
                    current_buffer = current_buffer[8+size:]
                    result.append((msgid, content))
                    if msgid == 'MDAT':
                        break
            time.sleep(0.001)
        return result

class SocketServer:
    def __init__(self,  host='127.0.0.1', port=12000):
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
    


if __name__ == '__main__':
    server = SocketServer()
    server.accept_connects(2)
    print('ok')