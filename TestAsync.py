import asyncio
import time

# 定义一个异步函数（协程），模拟io密集型操作
async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")

async def main():
    await asyncio.gather(*[count() for i in range(3)])

asyncio.run(main())