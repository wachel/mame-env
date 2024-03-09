import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import time
from typing import List
from mame_env.Console import ConsoleProcess
from mame_env.Client import AsyncClient
from mame_env.Server import AsyncServer
from mame_env.BaseType import Address, IOPort, StepAction
import asyncio

addresses = {
    "inited":Address("0x100004", 'u16'),# initialized if value is 0x24CA
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

class IOPorts:
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

start_action_sequence:List[StepAction] = [
    #start game
    StepAction(20, [IOPorts.COIN1]),
    StepAction(20, [IOPorts.START1]),
    StepAction(20, [IOPorts.P1_BUTTON1]),
    StepAction(20, [IOPorts.P1_BUTTON1]),
    StepAction(180, [IOPorts.P1_BUTTON1]),
    StepAction(20, [IOPorts.P1_BUTTON1]),
    #start select hero
    StepAction(10, [IOPorts.P1_BUTTON1]),
    StepAction(10, [IOPorts.P1_BUTTON1]),
    StepAction(10, [IOPorts.P1_BUTTON1]),
    #start order
    StepAction(350, [IOPorts.P1_BUTTON1]),
    StepAction(10, [IOPorts.P1_BUTTON1]),
    StepAction(10, [IOPorts.P1_BUTTON1]),
]

class Kof98Env():
    def __init__(self,client:AsyncClient):
        self.client = client

    async def start(self):
        self.client.send_memory_address(addresses)
        await self.do_start_steps(start_action_sequence)

    async def do_start_steps(self, steps:List[StepAction]):
        while True:
            data = await self.client.read_data()
            self.client.send_actions([])
            if data['inited'] == 0x24CA:
                break
        for step in steps:
            for i in range(step.wait_frames):
                data = await self.client.read_data()
                self.client.send_actions([])
            data = await self.client.read_data()
            self.client.send_actions(step.actions)

    def step(self, action):
        self.client.send_actions([])

    def reset(self, seed=None, options=None):
        pass

    def render(self):
        pass

    def close(self):
        pass

async def main():

    # start server
    server = AsyncServer()
    await server.start()

    client_num = 2

    # start all console
    for i in range(client_num):
        ConsoleProcess('roms', 'kof98', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', port=server.port, throttle=False, render=True)

    # wait console connect to server
    clients = await server.wait_clients(client_num)

    envs:List[Kof98Env] = []
    for client in clients:
        env = Kof98Env(client)
        envs.append(env)
    
    await asyncio.gather(*[env.start() for env in envs])

    while True:
        await asyncio.gather(*[env.client.read_data() for env in envs])
        for env in envs:
            env.step([])


if __name__ == '__main__':
    asyncio.run(main())