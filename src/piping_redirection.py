import os
from ui import print_error, print_success
from command_exec import run_command  # Reuse for sub-commands if needed

def handle_pipe(cmds, background=False):
    """Handle piping with system calls, colored errors."""
    if len(cmds) != 2:
        print_error("Only single pipe supported (e.g., cmd1 | cmd2).")
        return

    read_fd, write_fd = os.pipe()
    pid1 = os.fork()
    if pid1 == 0:
        os.close(read_fd)
        os.dup2(write_fd, 1)
        os.close(write_fd)
        os.execvp(cmds[0][0], cmds[0])
    else:
        pid2 = os.fork()
        if pid2 == 0:
            os.close(write_fd)
            os.dup2(read_fd, 0)
            os.close(read_fd)
            os.execvp(cmds[1][0], cmds[1])
        else:
            os.close(read_fd)
            os.close(write_fd)
            if not background:
                os.waitpid(pid1, 0)
                os.waitpid(pid2, 0)
                print_success("Pipe executed successfully.")
            else:
                print_info("Pipe running in background.")



def handle_redirection(cmd, redirect_type, file_path, background=False):
    """Handle I/O redirection with system calls."""
    pid = os.fork()
    if pid == 0:
        try:
            if redirect_type == '>':
                fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, 1)
                os.close(fd)
            elif redirect_type == '<':
                fd = os.open(file_path, os.O_RDONLY)
                os.dup2(fd, 0)
                os.close(fd)
            elif redirect_type == '>>':
                fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(fd, 1)
                os.close(fd)



            
            os.execvp(cmd[0], cmd)
        except FileNotFoundError:
            print_error(f"File '{file_path}' not found.")
            os._exit(1)
    else:
        if not background:
            os.waitpid(pid, 0)
            print_success(f"Redirection to '{file_path}' completed.")
        else:
            print_info(f"Redirection running in background.")
