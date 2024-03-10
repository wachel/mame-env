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
import random

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
    "p1_wins":Address("0x10A85E",'u8'),
    "p2_wins":Address("0x10A868",'u8'),
}

class IOPorts:
    START1 = IOPort(tag=":edge:joy:START", mask=1)
    START2 = IOPort(tag=":edge:joy:START", mask=4)
    COIN1 = IOPort(tag=":AUDIO_COIN", mask=1)
    COIN2 = IOPort(tag=":AUDIO_COIN", mask=2)
    SERVICE1 = IOPort(tag=":AUDIO_COIN", mask=4)
    SERVICE = IOPort(tag=":TEST", mask=128)
    P1_UP = IOPort(tag=":edge:joy:JOY1", mask=1)
    P1_DOWN = IOPort(tag=":edge:joy:JOY1", mask=2)
    P1_LEFT = IOPort(tag=":edge:joy:JOY1", mask=4)
    P1_RIGHT = IOPort(tag=":edge:joy:JOY1", mask=8)
    P1_A = IOPort(tag=":edge:joy:JOY1", mask=16)
    P1_B = IOPort(tag=":edge:joy:JOY1", mask=32)
    P1_C = IOPort(tag=":edge:joy:JOY1", mask=64)
    P1_D = IOPort(tag=":edge:joy:JOY1", mask=128)
    P2_UP = IOPort(tag=":edge:joy:JOY2", mask=1)
    P2_DOWN = IOPort(tag=":edge:joy:JOY2", mask=2)
    P2_LEFT = IOPort(tag=":edge:joy:JOY2", mask=4)
    P2_RIGHT = IOPort(tag=":edge:joy:JOY2", mask=8)
    P2_A = IOPort(tag=":edge:joy:JOY2", mask=16)
    P2_B = IOPort(tag=":edge:joy:JOY2", mask=32)
    P2_C = IOPort(tag=":edge:joy:JOY2", mask=64)
    P2_D = IOPort(tag=":edge:joy:JOY2", mask=128)

start_action_sequence:List[StepAction] = [
    #start game
    StepAction(20, [IOPorts.COIN1]),
    StepAction(20, [IOPorts.START1]),
    StepAction(20, [IOPorts.P1_A]),
    StepAction(20, [IOPorts.P1_A]),
    StepAction(180, [IOPorts.P1_A]),
    StepAction(20, [IOPorts.P1_A]),
    #start select hero
    StepAction(10, [IOPorts.P1_A]),
    StepAction(10, [IOPorts.P1_A]),
    StepAction(10, [IOPorts.P1_A]),
    #start order
    StepAction(350, [IOPorts.P1_A]),
    StepAction(10, [IOPorts.P1_A]),
    StepAction(10, [IOPorts.P1_A]),
]

move_actions = [
    [],
    [IOPorts.P1_UP],
    [IOPorts.P1_DOWN],
    [IOPorts.P1_LEFT], 
    [IOPorts.P1_RIGHT],
    [IOPorts.P1_UP, IOPorts.P1_LEFT],
    [IOPorts.P1_DOWN, IOPorts.P1_LEFT],
    [IOPorts.P1_UP, IOPorts.P1_RIGHT],
    [IOPorts.P1_DOWN, IOPorts.P1_RIGHT],
]

attack_actions = [
    [],
    [IOPorts.P1_A],
    [IOPorts.P1_B],
    [IOPorts.P1_C], 
    [IOPorts.P1_D],
    [IOPorts.P1_A, IOPorts.P1_B],
    [IOPorts.P1_C, IOPorts.P1_D],
    [IOPorts.P1_A, IOPorts.P1_B, IOPorts.P1_C],
]

class Kof98Env():
    def __init__(self,client:AsyncClient):
        self.client = client
        self.check_point_path = os.path.abspath("./checkpoint").replace("\\","/")
        self.wait_reset = 0

    async def start(self):
        self.client.send_memory_address(addresses)
        await self.do_start_steps(start_action_sequence)

    async def do_start_steps(self, steps:List[StepAction]):
        while True:
            await self.client.wait_frames(1)
            if self.client.data['inited'] == 0x24CA:
                break

        for step in steps:
            await self.client.wait_frames(step.wait_frames)
            await self.client.perform_actions_and_read_data(step.actions)

        while True:
            await self.client.wait_frames(1)
            if self.client.data['p1_health'] > 0:
                break
        
        self.client.execute_lua_string(f'manager.machine:save("{self.check_point_path}")')

    def step(self, action_codes):
        move_code, attack_code = action_codes
        self.client.perform_actions(move_actions[move_code] + attack_actions[attack_code])
        
        terminated = False
        if self.wait_reset > 0:
            self.wait_reset -= 1
        else:
            terminated = self.client.data['p1_wins'] > 0 or self.client.data['p2_wins'] > 0
        return [], 0, terminated, False, ''

    def reset(self, seed=None, options=None):
        self.client.execute_lua_string(f'manager.machine:load("{self.check_point_path}")')
        self.wait_reset = 3

async def main():
    # start server
    server = AsyncServer()
    await server.start()

    client_num = 1

    # start all console
    for i in range(client_num):
        ConsoleProcess(game_id='kof98', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', port=server.port, throttle=False, render=i==0)

    # wait console connect to server
    clients = await server.wait_clients(client_num)

    envs:List[Kof98Env] = []
    for client in clients:
        env = Kof98Env(client)
        envs.append(env)
    
    await asyncio.gather(*[env.start() for env in envs])

    while True:
        for env in envs:
            rand_move_code = random.randint(0,len(move_actions)-1)
            rand_attack_code = random.randint(0,len(attack_actions)-1)
            observation, reward, terminated, _, info = env.step([rand_move_code, rand_attack_code])
            if terminated:
                env.reset()
        await asyncio.gather(*[env.client.read_data() for env in envs])
        #await asyncio.sleep(0.001)


if __name__ == '__main__':
    asyncio.run(main())