import socket
import threading
import time
from typing import Callable, Dict, List
import struct
import queue

class Connect:
    def __init__(self, host='127.0.0.1', port=12000, connect_callback = None):
        self.host = host
        self.port = port
        self.server_thread = threading.Thread(target=self._start_listen_thread, args=())
        self.server_thread.start()
        self.next_sid = 0
        self.sessions:List[str, socket.socket] = {}
        self.connect_callback = connect_callback
        self.data_queue = queue.Queue()
    
    def send(self, sid:int, msgID:str, content:bytes):
        assert(len(msgID)==4)
        self.sessions[sid].send(struct.pack(f'4sI{len(content)}s', (msgID).encode(), len(content), content))

    def _start_listen_thread(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(1)

        while True:
            #accept new client
            client_socket, client_address = s.accept()
            sid = self.next_sid
            self.next_sid += 1
            self.sessions[sid] = client_socket

            if self.connect_callback:
                self.connect_callback(sid)
            #print(f"[+] Connection from {client_address[0]}:{client_address[1]}")

            # create a thread poll for client request
            client_thread = threading.Thread(target=self._handle_client_thread, args=(client_socket,sid))
            client_thread.start()

    def data_callback(self, sid, msgid, content):
        self.data_queue.put((sid, msgid, content))
    
    def pick_all_data(self, callback):
        while not self.data_queue.empty():
            sid, msgid, content = self.data_queue.get()
            callback(sid, msgid, content)

    def _handle_client_thread(self, client_socket:socket.socket, sid):
        current_buffer = bytes()
        while True:
            # recieve data from client
            current_buffer += client_socket.recv(1024)
            if len(current_buffer) >= 8:
                msgid,size = struct.unpack("4sI", current_buffer[0:8]) #msgid and length
                if len(current_buffer) >= 8 + size:
                    content = current_buffer[8:8+size]
                    current_buffer = current_buffer[8+size:]
                    self.data_callback(sid, msgid.decode(), content)

        # 关闭客户端连接
        client_socket.close()

if __name__ == '__main__':
    server = Connect()
    print('aaaa')
    time.sleep(100)