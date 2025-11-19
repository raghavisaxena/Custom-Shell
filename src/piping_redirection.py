import os
from ui import print_error, print_success
from command_exec import run_command  # Sub-commands dobara use karne ke liye


def handle_pipe(cmds, background=False):
    """System calls se piping handle karne ka function."""

    # Check kar rahe ki sirf 2 commands ho (cmd1 | cmd2)
    if len(cmds) != 2:
        print_error("Sirf single pipe supported hai (e.g., cmd1 | cmd2).")
        return

    # Pipe create karte hain → read aur write end milta hai
    read_fd, write_fd = os.pipe()

    # Pehla child process fork karte hain → yeh first command run karega
    pid1 = os.fork()
    if pid1 == 0:  # Child 1
        os.close(read_fd)         # Read wala end close; child 1 ko zarurat nahi
        os.dup2(write_fd, 1)      # stdout ko pipe ke write end pe redirect karo
        os.close(write_fd)        # Duplicate fd close kar do
        os.execvp(cmds[0][0], cmds[0])  # Pehli command execute hogi

    else:
        # Doosra child process fork karte hain → yeh second command run karega
        pid2 = os.fork()
        if pid2 == 0:  # Child 2
            os.close(write_fd)    # Write wala end close;child 2 ko nhi chahiye 
            os.dup2(read_fd, 0)   # stdin ko pipe ke read end se connect karte hain
            os.close(read_fd)     # Duplicate fd close
            os.execvp(cmds[1][0], cmds[1])  # Second command run karo

        else:
            # Parent process dono ends close karega
            os.close(read_fd)
            os.close(write_fd)

            # Agar background nahi hai toh wait karo dono processes ke liye
            if not background:
                os.waitpid(pid1, 0)
                os.waitpid(pid2, 0)
                print_success("Pipe successfully execute ho gaya.")
            else:
                print_info("Pipe background me run ho raha hai.")



def handle_redirection(cmd, redirect_type, file_path, background=False):
    """Input/output redirection handle karne ka function."""

    pid = os.fork()
    if pid == 0:  # Child process

        try:
            # Output overwrite redirection: command > file
            if redirect_type == '>':
                # File open karo (overwrite mode)
                fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, 1)  # stdout ko file me redirect karo
                os.close(fd)

            # Input redirection: command < file
            elif redirect_type == '<':
                fd = os.open(file_path, os.O_RDONLY)  # File read-only open karo
                os.dup2(fd, 0)  # stdin ko file se connect karo
                os.close(fd)

            # Output append redirection: command >> file
            elif redirect_type == '>>':
                fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(fd, 1)  # stdout ko append mode me file me redirect karo
                os.close(fd)

            # Ab actual command run kar do
            os.execvp(cmd[0], cmd)

        except FileNotFound
