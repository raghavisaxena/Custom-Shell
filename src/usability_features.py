import os
import glob  #helps in auto-completion
from ui import print_error, print_success

# Check if readline is available, if not, create dummy functions
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

# --- Command History ---
HISTORY_FILE = os.path.expanduser("~/.customshell_history")

# --- Alias Management ---
ALIASES_FILE = os.path.expanduser("~/.customshell_aliases")

def setup_readline():
    """Enable history and autocompletion for the CLI."""
    if READLINE_AVAILABLE:
        if not os.path.exists(HISTORY_FILE):
            open(HISTORY_FILE, 'w').close()
        readline.read_history_file(HISTORY_FILE)
        readline.set_history_length(1000)
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

def save_history(command):
    """Append a command to the history file."""
    if READLINE_AVAILABLE:
        readline.add_history(command)
        readline.write_history_file(HISTORY_FILE)
    else:
        # Fallback for non-readline environments
        with open(HISTORY_FILE, 'a') as f:
            f.write(command + '\n')


def load_aliases():
    """Load aliases from the alias file into a dictionary."""
    aliases = {}
    if os.path.exists(ALIASES_FILE):
        try:
            with open(ALIASES_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        aliases[key.strip()] = value.strip().strip("'\"")
        except Exception as e:
            print_error(f"Failed to load aliases: {e}")
    return aliases


def save_aliases(aliases):
    """Save the entire aliases dictionary to the file, overwriting it."""
    try:
        with open(ALIASES_FILE, 'w') as f:
            for name, command in aliases.items():
                f.write(f"{name}='{command}'\n")
        return True
    except Exception as e:
        print_error(f"Failed to save aliases: {e}")
        return False


def expand_alias(command_line, aliases):
    """Expand the first part of a command if it's an alias."""
    parts = command_line.split(maxsplit=1)
    if not parts:
        return ""
    cmd = parts[0]
    if cmd in aliases:
        expanded_cmd = aliases[cmd]
        if len(parts) > 1:
            return f"{expanded_cmd} {parts[1]}"
        else:
            return expanded_cmd
    return command_line


# --- Autocompletion Logic (for readline) ---
COMMANDS = [
    'help', 'cd', 'exit', 'history', 'alias', 'pwd', 'jobs',
    'ls', 'cat', 'grep', 'echo', 'touch', 'mkdir', 'mv', 'rm', 'cp'
]

def completer(text, state):
    """Autocompletion function for commands and file paths."""
    line = readline.get_line_buffer()
    begin = readline.get_begidx()
    
    if begin == 0:
        options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
    else:
        options = glob.glob(text + '*')
        options = [o + '/' if os.path.isdir(o) else o for o in options]

    if state < len(options):
        return options[state]
    else:
        return None
