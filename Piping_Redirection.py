import os  
from ui import print_error, print_success  
from command_exec import run_command  # Used if sub-commands need to be executed

def handle_pipe(cmds, background=False):
    """Handle piping between two commands using system calls."""
    
    # Ensure exactly two commands are provided (cmd1 | cmd2)
    if len(cmds) != 2:
        print_error("Only single pipe supported (e.g., cmd1 | cmd2).")
        return

    # Create a pipe → gives two file descriptors: one for reading, one for writing
    read_fd, write_fd = os.pipe()

    # First fork → create child process for the first command
    pid1 = os.fork()

    # ----- CHILD PROCESS 1 (executes cmds[0]) -----
    if pid1 == 0:
        # Close unused read end in first child (cmd1 writes into pipe)
        os.close(read_fd)

        # Redirect child's STDOUT to pipe's write end
        os.dup2(write_fd, 1)

        # Close original write end (not needed after dup2)
        os.close(write_fd)

        # Execute the first command (cmd1)
        os.execvp(cmds[0][0], cmds[0])

    # ----- PARENT PROCESS -----
    else:
        # Second fork → create child process for the second command
        pid2 = os.fork()

        # ----- CHILD PROCESS 2 (executes cmds[1]) -----
        if pid2 == 0:
            # Close unused write end in second child (cmd2 reads from pipe)
            os.close(write_fd)

            # Redirect child's STDIN to pipe's read end
            os.dup2(read_fd, 0)

            # Close original read end (not needed after dup2)
            os.close(read_fd)

            # Execute the second command (cmd2)
            os.execvp(cmds[1][0], cmds[1])

        # ----- PARENT PROCESS (after creating both children) -----
        else:
            # Parent closes both pipe ends (children will handle communication)
            os.close(read_fd)
            os.close(write_fd)

            # If process is not running in background → wait for both children
            if not background:
                os.waitpid(pid1, 0)  # wait for first command
                os.waitpid(pid2, 0)  # wait for second command
                print_success("Pipe executed successfully.")
            else:
                # For background processes (cmd1 | cmd2 &)
                print_info("Pipe running in background.")


def handle_redirection(cmd, redirect_type, file_path, background=False):
    """Handle input/output redirection using system calls."""
    
    # Fork → child will execute command with redirection
    pid = os.fork()

    # ----- CHILD PROCESS -----
    if pid == 0:
        try:
            # Output redirection with overwrite (>)
            if redirect_type == '>':
                # Open file for writing → create if not exists, truncate otherwise
                fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)

                # Redirect STDOUT to file
                os.dup2(fd, 1)
                os.close(fd)

            # Input redirection (<)
            elif redirect_type == '<':
                # Open file for reading only
                fd = os.open(file_path, os.O_RDONLY)

                # Redirect STDIN to file
                os.dup2(fd, 0)
                os.close(fd)

            # Output redirection with append (>>)
            elif redirect_type == '>>':
                # Open file in append mode → create if not exists
                fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)

                # Redirect STDOUT to file
                os.dup2(fd, 1)
                os.close(fd)

            # Execute the actual command with modified stdin/stdout
            os.execvp(cmd[0], cmd)

        except FileNotFoundError:
            # If file for input redirection doesn't exist
            print_error(f"File '{file_path}' not found.")
            os._exit(1)  # exit child safely

    # ----- PARENT PROCESS -----
    else:
        # If not a background job → wait for child to finish
        if not background:
            os.waitpid(pid, 0)
            print_success(f"Redirection to '{file_path}' completed.")
        else:
            # Background mode → do not wait
            print_info(f"Redirection running in background.")
