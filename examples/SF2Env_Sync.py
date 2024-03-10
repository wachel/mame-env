import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import time
from typing import List
from mame_env.Console import ConsoleProcess
from mame_env.Client import AsyncClient
from mame_env.Server import AsyncServer, SocketServer
from mame_env.BaseType import Address, IOPort, StepAction
import asyncio
import random
import concurrent.futures

addresses = {
    "time": Address('0xFF8ACE', 'u8'),
    "healthP1": Address('0xFF83F1', 'u8'),
    "redhealthP1": Address('0xFF83F3', 'u8'),
    "healthP2": Address('0xFF86F1', 'u8'),
    "redhealthP2": Address('0xFF86F3', 'u8'),
}

class IOPorts: 
    COIN1 = IOPort(tag=":IN0", mask=1)
    COIN2 = IOPort(tag=":IN0", mask=2)
    SERVICE1 = IOPort(tag=":IN0", mask=4)
    START1 = IOPort(tag=":IN0", mask=16)
    START2 = IOPort(tag=":IN0", mask=32)
    SERVICE = IOPort(tag=":IN0", mask=64)
    P1_JOYSTICK_RIGHT = IOPort(tag=":IN1", mask=1)
    P1_JOYSTICK_LEFT = IOPort(tag=":IN1", mask=2)
    P1_JOYSTICK_DOWN = IOPort(tag=":IN1", mask=4)
    P1_JOYSTICK_UP = IOPort(tag=":IN1", mask=8)
    P1_BUTTON1 = IOPort(tag=":IN1", mask=16)
    P1_BUTTON2 = IOPort(tag=":IN1", mask=32)
    P1_BUTTON3 = IOPort(tag=":IN1", mask=64)
    P1_BUTTON4 = IOPort(tag=":IN2", mask=1)
    P1_BUTTON5 = IOPort(tag=":IN2", mask=2)
    P1_BUTTON6 = IOPort(tag=":IN2", mask=4)
    P2_JOYSTICK_RIGHT = IOPort(tag=":IN1", mask=256)
    P2_JOYSTICK_LEFT = IOPort(tag=":IN1", mask=512)
    P2_JOYSTICK_DOWN = IOPort(tag=":IN1", mask=1024)
    P2_JOYSTICK_UP = IOPort(tag=":IN1", mask=2048)
    P2_BUTTON1 = IOPort(tag=":IN1", mask=4096)
    P2_BUTTON2 = IOPort(tag=":IN1", mask=8192)
    P2_BUTTON3 = IOPort(tag=":IN1", mask=16384)
    P2_BUTTON4 = IOPort(tag=":IN2", mask=16)
    P2_BUTTON5 = IOPort(tag=":IN2", mask=32)
    P2_BUTTON6 = IOPort(tag=":IN2", mask=64) 

start_action_sequence:List[StepAction] = [
    #start game
    StepAction(300, [IOPorts.COIN1]),
    StepAction(700, [IOPorts.START1]),
    StepAction(200, [IOPorts.P1_BUTTON1]),
    StepAction(200, [IOPorts.P1_BUTTON1]),
]

move_actions = [
    [],
    [IOPorts.P1_JOYSTICK_UP],
    [IOPorts.P1_JOYSTICK_DOWN],
    [IOPorts.P1_JOYSTICK_LEFT], 
    [IOPorts.P1_JOYSTICK_RIGHT],
    [IOPorts.P1_JOYSTICK_UP, IOPorts.P1_JOYSTICK_LEFT],
    [IOPorts.P1_JOYSTICK_DOWN, IOPorts.P1_JOYSTICK_LEFT],
    [IOPorts.P1_JOYSTICK_UP, IOPorts.P1_JOYSTICK_RIGHT],
    [IOPorts.P1_JOYSTICK_DOWN, IOPorts.P1_JOYSTICK_RIGHT],
]

attack_actions = [
    [],
    [IOPorts.P1_BUTTON1],
    [IOPorts.P1_BUTTON2],
    [IOPorts.P1_BUTTON3], 
    [IOPorts.P1_BUTTON4],
    [IOPorts.P1_BUTTON5],
    [IOPorts.P1_BUTTON6],
    [IOPorts.P1_BUTTON1, IOPorts.P1_BUTTON2, IOPorts.P1_BUTTON3],
]

class SF2Env():
    def __init__(self,client:AsyncClient):
        self.client = client
        self.check_point_path = os.path.abspath("./checkpoint").replace("\\","/")
        self.wait_reset = 0

    def start(self):
        self.client.send_memory_address(addresses)
        self.do_start_steps(start_action_sequence)

    def do_start_steps(self, steps:List[StepAction]):
        for step in steps:
            self.client.wait_frames(step.wait_frames)
            self.client.perform_actions_and_read_data(step.actions)
            self.client.perform_actions_and_read_data(step.actions)

        while True:
            self.client.wait_frames(1)
            if self.client.data['healthP1'] > 0:
                break
        
        self.client.execute_lua_string(f'manager.machine:save("{self.check_point_path}")')

    def step(self, action_codes):
        move_code, attack_code = action_codes
        self.client.perform_actions(move_actions[move_code] + attack_actions[attack_code])
        
        terminated = False
        if self.wait_reset > 0:
            self.wait_reset -= 1
        else:
            terminated = self.client.data['time'] < 0 or self.client.data['healthP1'] <=0 or self.client.data['healthP2'] <= 0
        return [], 0, terminated, False, ''

    def reset(self, seed=None, options=None):
        self.client.execute_lua_string(f'manager.machine:load("{self.check_point_path}")')
        self.wait_reset = 3

def main():
    # start server
    server = SocketServer()
    server.start()

    client_num = 2

    # start all console
    for i in range(client_num):
        ConsoleProcess('sf2', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', port=server.port, throttle=False, render=True)

    # wait console connect to server
    clients = server.wait_clients(client_num)

    envs:List[SF2Env] = []
    for client in clients:
        env = SF2Env(client)
        envs.append(env)
    
    def start_all(env):
        return env.start()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(start_all, envs))

    while True:
        for env in envs:
            rand_move_code = random.randint(0,len(move_actions)-1)
            rand_attack_code = random.randint(0,len(attack_actions)-1)
            observation, reward, terminated, _, info = env.step([rand_move_code, rand_attack_code])
            if terminated:
                env.reset()
        for env in envs:
            env.client.read_data() 

    server.stop()

if __name__ == '__main__':
    asyncio.run(main())