import asyncio
from typing import List
from Client import AsyncClient

class AsyncServer:
    def __init__(self, host='127.0.0.1', port=12001):
        self.host = host
        self.port = port
        self.clients_connects = []
    
    async def start(self):
        server = await asyncio.start_server(self.handle_client_connect, self.host, self.port)
        server_task = asyncio.create_task(server.serve_forever())
    
    def handle_client_connect(self, reader, writer):
        self.clients_connects.append((reader, writer))

    async def wait_clients(self, total_num)->List[AsyncClient]:
        while len(self.clients_connects) < total_num:
            await asyncio.sleep(0)
        clients = []
        for reader, writer in self.clients_connects:
            clients.append(AsyncClient(reader, writer))
        return clients