import time
from typing import List
from BaseType import IOPort, Address
from Console import ConsoleProcess
from Client import AsyncClient, Client
from Server import AsyncServer, SocketServer
import asyncio

kof_addresses = {
    "p1_health": Address('0x108239', 's8'),#0~103
    "p2_health": Address('0x108439', 's8'),
    "p1_direction": Address('0x108131', 's8'),#right=1，left=0
    "p2_direction": Address('0x108331', 's8'),#right=1，left=0
    "p1_combocounter": Address('0x1084b0', 's8'),
    "p2_combocounter": Address('0x1082b0', 's8'),
    "p1_gx":Address("0x108118",'u16'),#0x20-0x2E0 ,global pose
    "p2_gx":Address("0x108318",'u16'),#0x20-0x2E0 
    "p1_x":Address("0x108124",'u16'),#0x20~0x120 ,screenpos
    "p2_x":Address("0x108324",'u16'),
    "p1_y":Address("0x108121",'u8'),#0~11
    "p2_y":Address("0x108321",'u8'),
    "p1_state":Address("0x108172",'u16'),
    "p2_state":Address("0x108372",'u16'),
    "p1_xspeed":Address("0x108144",'s16'),#-6~+6
    "p2_xspeed":Address("0x108344",'s16'),
    "p1_power":Address("0x1081E8",'u8'),
    "p2_power":Address("0x1083E8",'u8'),
    "p1_powercount":Address("0x10825e",'u8'),
    "p2_powercount":Address("0x10845e",'u8'),
    "p1_character":Address("0x108171",'u8'),
    "p2_character":Address("0x108371",'u8'),

}
class KofIOPorts:
    START1 = IOPort(tag=":edge:joy:START", mask=1)
    START2 = IOPort(tag=":edge:joy:START", mask=4)
    COIN1 = IOPort(tag=":AUDIO_COIN", mask=1)
    COIN2 = IOPort(tag=":AUDIO_COIN", mask=2)
    SERVICE1 = IOPort(tag=":AUDIO_COIN", mask=4)
    SERVICE = IOPort(tag=":TEST", mask=128)
    P1_JOYSTICK_UP = IOPort(tag=":edge:joy:JOY1", mask=1)
    P1_JOYSTICK_DOWN = IOPort(tag=":edge:joy:JOY1", mask=2)
    P1_JOYSTICK_LEFT = IOPort(tag=":edge:joy:JOY1", mask=4)
    P1_JOYSTICK_RIGHT = IOPort(tag=":edge:joy:JOY1", mask=8)
    P1_BUTTON1 = IOPort(tag=":edge:joy:JOY1", mask=16)
    P1_BUTTON2 = IOPort(tag=":edge:joy:JOY1", mask=32)
    P1_BUTTON3 = IOPort(tag=":edge:joy:JOY1", mask=64)
    P1_BUTTON4 = IOPort(tag=":edge:joy:JOY1", mask=128)
    P2_JOYSTICK_UP = IOPort(tag=":edge:joy:JOY2", mask=1)
    P2_JOYSTICK_DOWN = IOPort(tag=":edge:joy:JOY2", mask=2)
    P2_JOYSTICK_LEFT = IOPort(tag=":edge:joy:JOY2", mask=4)
    P2_JOYSTICK_RIGHT = IOPort(tag=":edge:joy:JOY2", mask=8)
    P2_BUTTON1 = IOPort(tag=":edge:joy:JOY2", mask=16)
    P2_BUTTON2 = IOPort(tag=":edge:joy:JOY2", mask=32)
    P2_BUTTON3 = IOPort(tag=":edge:joy:JOY2", mask=64)
    P2_BUTTON4 = IOPort(tag=":edge:joy:JOY2", mask=128)

class Kof98Env():
    def __init__(self,client:AsyncClient):
        self.client = client
        self.client.send_memory_address(kof_addresses)

    async def do_start_commands(self):
        for i in range(2000):
            await self.client.read_data()
            await asyncio.sleep(0)
            self.client.send_actions([])
        self.client.send_actions([KofIOPorts.COIN1])
        self.client.send_actions([KofIOPorts.COIN1])
        self.client.send_actions([KofIOPorts.COIN1])
        for i in range(100):
            await self.client.read_data()
            self.client.send_actions([])
        self.client.send_actions([KofIOPorts.START1])
        self.client.send_actions([KofIOPorts.START1])
        self.client.send_actions([KofIOPorts.START1])
        for i in range(100):
            await self.client.read_data()
            self.client.send_actions([])
        self.client.send_actions([KofIOPorts.P1_BUTTON1])
        self.client.send_actions([KofIOPorts.P1_BUTTON1])
        for i in range(10):
            await self.client.read_data()
            self.client.send_actions([])
        self.client.send_actions([KofIOPorts.P1_BUTTON1])
        self.client.send_actions([KofIOPorts.P1_BUTTON1])

    def step(self, action):
        self.client.send_actions([])

    def reset(self, seed=None, options=None):
        pass

    def render(self):
        pass

    def close(self):
        pass

async def main():
    server = AsyncServer()
    await server.start()

    client_num = 1

    consoles = []
    for i in range(client_num):
        consoles.append(ConsoleProcess('roms', 'kof98', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', port=server.port, render=True))

    clients = await server.wait_clients(client_num)
    print('all clients connected')

    envs:List[Kof98Env] = []
    for client in clients:
        client.send_memory_address(kof_addresses)
        envs.append(Kof98Env(client))


    await asyncio.gather(*[env.do_start_commands() for env in envs])

    while True:
        await asyncio.gather(*[client.read_data() for client in clients])
        for env in envs:
            envs[i].step([])


if __name__ == '__main__':
    asyncio.run(main())