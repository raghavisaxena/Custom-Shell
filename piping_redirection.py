# piping_redirection.py
import os
import sys

class PipeRedirectHandler:
    def __init__(self):
        pass

    def parse_command(self, command_str):
        # Returns list of commands split by pipe
        return [cmd.strip() for cmd in command_str.split('|')]

    def parse_redirection(self, cmd):
        # Returns (cmd_args, input_file, output_file)
        parts = cmd.split()
        cmd_args = []
        input_file = None
        output_file = None
        i = 0
        while i < len(parts):
            if parts[i] == '<':
                if i + 1 < len(parts):
                    input_file = parts[i+1]
                    i += 2
                else:
                    print("Syntax error near unexpected token `<`")
                    return None, None, None
            elif parts[i] == '>':
                if i + 1 < len(parts):
                    output_file = parts[i+1]
                    i += 2
                else:
                    print("Syntax error near unexpected token `>`")
                    return None, None, None
            else:
                cmd_args.append(parts[i])
                i += 1
        return cmd_args, input_file, output_file

    def run_pipeline(self, commands, executor):
        n = len(commands)
        pipe_fds = []

        for i in range(n - 1):
            pipe_fds.append(os.pipe())

        for i, cmd in enumerate(commands):
            cmd_args, input_file, output_file = self.parse_redirection(cmd)
            if cmd_args is None:
                return

            pid = os.fork()
            if pid == 0:
                # Child process

                # Input redirection
                if input_file:
                    try:
                        fd_in = os.open(input_file, os.O_RDONLY)
                        os.dup2(fd_in, 0)
                        os.close(fd_in)
                    except Exception as e:
                        print(f"Error opening input file {input_file}: {e}")
                        os._exit(1)

                # Output redirection
                if output_file:
                    try:
                        fd_out = os.open(output_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                        os.dup2(fd_out, 1)
                        os.close(fd_out)
                    except Exception as e:
                        print(f"Error opening output file {output_file}: {e}")
                        os._exit(1)

                # Setup pipes
                if i > 0:
                    # Not first command: replace stdin with read end of previous pipe
                    os.dup2(pipe_fds[i-1][0], 0)
                if i < n - 1:
                    # Not last command: replace stdout with write end of current pipe
                    os.dup2(pipe_fds[i][1], 1)

                # Close all pipe fds in child
                for r, w in pipe_fds:
                    os.close(r)
                    os.close(w)

                try:
                    os.execvp(cmd_args[0], cmd_args)
                except FileNotFoundError:
                    print(f"{cmd_args[0]}: command not found")
                except Exception as e:
                    print(f"Error executing {cmd_args[0]}: {e}")
                os._exit(1)
            # Parent continues loop

        # Parent closes all pipe fds
        for r, w in pipe_fds:
            os.close(r)
            os.close(w)

        # Wait for all children
        for _ in commands:
            os.wait()
