# main.py
from core_shell import CoreShell
from command_exec import CommandExecutor
from piping_redirection import PipeRedirectHandler
from usability_features import UsabilityFeatures

import shlex

def main():
    core = CoreShell()
    executor = CommandExecutor()
    pipe_handler = PipeRedirectHandler()
    usability = UsabilityFeatures()

    while True:
        # Use colored prompt from usability features if you want
        try:
            # Read input with alias expansion
            raw_input = input(usability.colored_prompt())
        except EOFError:
            print("\nExiting shell.")
            break
        except KeyboardInterrupt:
            print()
            continue

        if not raw_input.strip():
            continue

        # Add to history
        usability.add_history(raw_input)

        # Expand aliases
        command_line = usability.expand_aliases(raw_input)

        # Check for built-in commands first (only if no pipes)
        if '|' not in command_line:
            parts = shlex.split(command_line)
            if not parts:
                continue
            cmd = parts[0]
            args = parts[1:]

            builtin_result = core.handle_builtin(cmd, args)
            if builtin_result == "exit":
                break
            elif builtin_result == "handled":
                continue

            # Check for background execution
            background = False
            if args and args[-1] == '&':
                background = True
                args = args[:-1]

            # Execute single command with possible redirection
            # Check for redirection symbols
            if '>' in command_line or '<' in command_line:
                # Use pipe handler to run single command with redirection
                pipe_handler.run_pipeline([command_line], executor)
            else:
                executor.execute(cmd, args, background)
        else:
            # Pipeline present
            commands = pipe_handler.parse_command(command_line)
            pipe_handler.run_pipeline(commands, executor)

if __name__ == "__main__":
    main()