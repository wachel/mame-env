import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from mame_env.Console import ConsoleProcess
import time

ConsoleProcess('roms','sf2', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', lua_script='print_ioport.lua', render=True, throttle=True)

time.sleep(50)