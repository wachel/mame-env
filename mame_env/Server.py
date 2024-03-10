import asyncio
from typing import List,Tuple
from .Client import AsyncClient
from asyncio import StreamWriter, StreamReader

class AsyncServer:
    def __init__(self, host='127.0.0.1', port=12001):
        self.host = host
        self.port = port
        self.clients_connects:List[Tuple[StreamReader, StreamWriter]] = []
    
    async def start(self):
        self.server = await asyncio.start_server(self.handle_client_connect, self.host, self.port)
        self.server_task = asyncio.create_task(self.server.serve_forever())
    
    def stop(self):
        for reader,writer in self.clients_connects:
            writer.close()
        self.server_task.cancel()
        self.server.close()
    
    def handle_client_connect(self, reader, writer):
        self.clients_connects.append((reader, writer))

    async def wait_clients(self, total_num)->List[AsyncClient]:
        while len(self.clients_connects) < total_num:
            await asyncio.sleep(0)
        clients = []
        for i,(reader, writer) in enumerate(self.clients_connects):
            clients.append(AsyncClient(i, reader, writer))
        return clients