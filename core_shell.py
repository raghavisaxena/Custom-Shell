# core_shell.py
import os

class CoreShell:
    def __init__(self):
        pass

    def get_prompt(self):
        cwd = os.getcwd()
        user = os.getenv("USER") or "user"
        # Simple prompt: username and current directory
        return f"{user}:{cwd} $ "

    def handle_builtin(self, cmd, args):
        if cmd == "exit":
            print("Exiting shell.")
            return "exit"
        elif cmd == "cd":
            if len(args) == 0:
                target_dir = os.path.expanduser("~")
            else:
                target_dir = args[0]
            try:
                os.chdir(target_dir)
            except FileNotFoundError:
                print(f"cd: no such file or directory: {target_dir}")
            except NotADirectoryError:
                print(f"cd: not a directory: {target_dir}")
            except PermissionError:
                print(f"cd: permission denied: {target_dir}")
            return "handled"
        return None

    def read_command(self):
        try:
            inp = input(self.get_prompt())
            return inp
        except EOFError:
            print("\nExiting shell.")
            return "exit"
        except KeyboardInterrupt:
            print()  # newline on Ctrl+C
            return ""
