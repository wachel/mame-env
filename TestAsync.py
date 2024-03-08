import asyncio
import time

# 定义一个异步函数（协程），模拟io密集型操作
async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")

async def get_num():
    return 999

async def handle_echo(reader, writer):
    print('client connect')

async def start_server():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 5555)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    server_task = asyncio.create_task(server.serve_forever())

async def main():
    await start_server()

    print(await get_num())

    print('aaaa')
    await asyncio.sleep(100)

asyncio.run(main())

