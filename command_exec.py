# command_exec.py
import os
import sys

class CommandExecutor:
    def __init__(self):
        pass

    def execute(self, cmd, args, background=False):
        pid = os.fork()
        if pid == 0:
            # Child process
            try:
                os.execvp(cmd, [cmd] + args)
            except FileNotFoundError:
                print(f"{cmd}: command not found")
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
            os._exit(1)
        else:
            # Parent process
            if not background:
                _, status = os.waitpid(pid, 0)
            else:
                print(f"[{pid}] running in background")