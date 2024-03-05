import time
from typing import List
from BaseType import Action, Address
from Console import ConsoleProcess
from Server import Server

kof_addresses = {
    "p1_health": Address('0x108239', 's8'),#0~103
    "p2_health": Address('0x108439', 's8'),
}
kof_actions = {
    '':[],
    # 'a':[Action(':DSW','Free Play')],
    # 'a':[Action(':DSW','COMM Setting (Cabinet No.)')],
    # 'a':[Action(':DSW','Setting Mode')],
    # 'a':[Action(':DSW','Freeze')],
    # 'a':[Action(':DSW','Cabinet')],
    # 'a':[Action(':DSW','COMM Setting (Link Enable)')],
    # 'a':[Action(':DSW','Controller')],
    # 'a':[Action(':TEST','Service Mode')],
    # 'a':[Action(':edge:joy:JOY1','P1 D')],
    # 'a':[Action(':edge:joy:JOY1','P1 C')],
    'a':[Action(':edge:joy:JOY1','P1 A')],
    # 'a':[Action(':edge:joy:JOY1','P1 B')],
    # 'a':[Action(':edge:joy:JOY2','P2 D')],
    # 'a':[Action(':edge:joy:JOY2','P2 C')],
    # 'a':[Action(':edge:joy:JOY2','P2 A')],
    # 'a':[Action(':edge:joy:JOY2','P2 B')],
}


server = Server(addresses=kof_addresses)

client_num = 2
for i in range(client_num):
    console = ConsoleProcess('roms', 'kof98', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', port=server.connect.port)

while server.client_num < client_num:
    time.sleep(0.01)

frame = 0
while True:
    frame += 1
    all_mem_data = server.read_mem_data()
    all_actions:List[List[Action]] = [[]]*server.client_num
    # for i, mem_data in enumerate(all_mem_data):
    #     all_actions[i] = actions = []
    #     if i%2==0:
    #         if (frame//5)%2==0:
    #             actions.extend(kof_actions['a'])
    #     else:
    #         if (frame//10)%2==0:
    #             actions.extend(kof_actions['a'])

    server.send_actions(all_actions)