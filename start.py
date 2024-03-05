import time
from typing import List
from BaseType import Action, Address
from Console import ConsoleProcess
from Connect import SocketConnect, SocketServer

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


server = SocketServer()

client_num = 28
for i in range(client_num):
    console = ConsoleProcess('roms', 'kof98', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', port=server.port, render=i==0)

client_sockets = server.accept_connects(client_num)

mem_address_buff = '|'.join([f'{name},{addr.address},{addr.type}' for name, addr in kof_addresses.items()])
for client in client_sockets:
    client.send('ADDR', mem_address_buff)

frame = 0
while True:
    frame += 1
    for client in client_sockets:
        msgs = client.recive()
        for msgid, content in msgs:
            if msgid == 'MDAT':
                actions = []
                if (frame//5)%2==0:
                    actions.extend(kof_actions['a'])
                action_buff = '|'.join([f'{act.port}+{act.field}' for act in actions])
                client.send('ACTN', action_buff)

print('connected')