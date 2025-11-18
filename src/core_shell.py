import os
import sys
import shlex
import glob
from ui import get_colored_prompt, print_banner, print_error, print_success, print_info
from usability_features import setup_readline, save_history, save_aliases, expand_alias, ALIASES_FILE, HISTORY_FILE
from command_exec import run_command, get_jobs
from piping_redirection import handle_pipe, handle_redirection

def handle_builtin(command, args, aliases):
    """Handle built-in commands and return True if handled."""
    if command == 'exit':
        print_info("Goodbye! Exiting CustomShell.")
        sys.exit(0)

    elif command == 'cd':
        try:
            path = args[0] if args else os.path.expanduser("~")
            os.chdir(path)
        except FileNotFoundError:
            print_error(f"Directory not found: {path}")
        except PermissionError:
            print_error(f"Permission denied: {path}")
        except IndexError:
            os.chdir(os.path.expanduser("~"))
        return True

    elif command == 'jobs':
        jobs = get_jobs()
        if not jobs:
            print_info("No background jobs.")
        else:
            for i, job in enumerate(jobs):
                print(f"[{i+1}] {job['pid']} {job['status']} {job['command']}")
        return True

    elif command == 'alias':
        if not args:
            if not aliases:
                print_info("No aliases defined.")
            for name, cmd in aliases.items():
                print(f"{name}='{cmd}'")
        elif '=' in args[0]:
            name, cmd = args[0].split('=', 1)
            aliases[name] = cmd.strip("'\"")
            if save_aliases(aliases):
                print_success(f"Alias '{name}' set.")
        else:
            print_error("Usage: alias [name='command']")
        return True

    elif command == 'unalias':
        if len(args) == 1:
            name = args[0]
            if name in aliases:
                del aliases[name]
                if save_aliases(aliases):
                    print_success(f"Alias '{name}' removed.")
            else:
                print_error(f"Alias not found: {name}")
        else:
            print_error("Usage: unalias [name]")
        return True

    elif command == 'history':
        try:
            with open(HISTORY_FILE, 'r') as f:
                for i, line in enumerate(f.readlines()):
                    print(f"{i+1} {line.strip()}")
        except FileNotFoundError:
            print_info("No history yet.")
        return True

    elif command == 'help':
        print_banner()
        print_info("Built-in commands: exit, cd, jobs, alias, unalias, history, help")
        return True
        
    return False

def shell_loop(aliases):
    """Main interactive loop for the command-line shell."""
    setup_readline()
    print_banner()

    while True:
        try:
            raw_inp = input(get_colored_prompt()).strip()
            if not raw_inp:
                continue

            save_history(raw_inp)
            inp = expand_alias(raw_inp, aliases)
            background = inp.endswith('&')
            if background:
                inp = inp[:-1].strip()

            args = shlex.split(inp)
            if not args:
                continue

            command = args[0]
            expanded_args = []
            if len(args) > 1:
                for arg in args[1:]:
                    if any(c in arg for c in '*?['):
                        glob_matches = glob.glob(arg)
                        if glob_matches:
                            expanded_args.extend(glob_matches)
                        else:
                            expanded_args.append(arg)
                    else:
                        expanded_args.append(arg)
            
            if handle_builtin(command, expanded_args, aliases):
                continue

            run_command(command, expanded_args, background)

        except KeyboardInterrupt:
            print() 
            print_info("Interrupted. Type 'exit' to quit.")
        except EOFError:
            print() 
            print_info("Goodbye!")
            break
        except Exception as e:
            print_error(f"An unexpected error occurred: {e}")
