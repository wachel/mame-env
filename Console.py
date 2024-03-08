import atexit
import os
import subprocess
import logging
import time

class ConsoleProcess(object):
    def __init__(self, roms_path, game_id, render=True, throttle=False, frame_skip=0, sound=False, mame_bin_path='mame', lua_script = 'bridge.lua', other_args = '', ip='127.0.0.1', port=12000):
        atexit.register(self.close)
        self.logger = logging.getLogger("Console")

        env = os.environ.copy()
        env['SERVER_PORT'] = str(port)
        env['SERVER_IP'] = ip

        mame_path = os.path.dirname(os.path.abspath(mame_bin_path))
        lua_path = os.path.abspath('./lua')

        command = f'{mame_bin_path} {game_id} -rompath "{os.path.abspath(roms_path)}" -skip_gameinfo -window -nomaximize -noverbose -nojoy'
        command += f' -autoboot_script {lua_path}/{lua_script}'
        if not render:
            command += " -video none -seconds_to_run 10000000"

        if throttle:
            command += " -throttle"
        else:
            command += " -nothrottle"

        if frame_skip>0:
            command += " -frameskip "+str(frame_skip)

        if not sound:
            command += " -sound none"
        
        command += ' ' + other_args

        self.process = subprocess.Popen(command, cwd=mame_path,env=env)

    # Safely kills the emulator process
    def close(self):
        self.process.kill()
        try:
            self.process.wait(timeout=3)
        except Exception as e:
            error = "Failed to close emulator console"
            self.logger.error(error, e)
            raise EnvironmentError(error)
