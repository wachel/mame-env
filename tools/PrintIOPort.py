from Console import ConsoleProcess
import time

ConsoleProcess('roms','kof98', mame_bin_path='G:\games\mame0256b_64bit\mame.exe', lua_script='print_ioport.lua', render=True)

time.sleep(100)