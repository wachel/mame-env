import socket
from typing import List
from Client import Client

class SocketServer:
    def __init__(self, host='127.0.0.1', port=12001):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.host = host
        self.port = port
    
    def accept_client_connects(self, total_num)->List[Client]:
        clients = []
        for i in range(total_num):
            s, address = self.socket.accept()
            clients.append(Client(s))
        return clients
    