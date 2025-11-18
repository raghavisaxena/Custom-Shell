import os
import re

# Regex to find and remove ANSI escape codes
ANSI_ESCAPE_REGEX = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')

# --- ANSI Color Codes ---
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Basic Colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright/Light Colors (often used for prompts)
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    # UI-specific (for clarity)
    PROMPT_USER = BRIGHT_CYAN
    PROMPT_DIR = BRIGHT_GREEN
    PROMPT_SYMBOL = BRIGHT_BLUE
    INFO = BRIGHT_YELLOW
    SUCCESS = BRIGHT_GREEN
    ERROR = BRIGHT_RED

# --- UI Functions ---
def get_colored_prompt():
    """Return a beautifully colored shell prompt."""
    # Get user, host, and current directory
    user = os.environ.get('USER', 'user')
    hostname = os.uname().nodename if hasattr(os, 'uname') else 'host'
    cwd = os.getcwd()

    # Shorten path for readability (e.g., /home/user -> ~)
    home = os.path.expanduser('~')
    if cwd.startswith(home):
        cwd = '~' + cwd[len(home):]
    
    # Truncate long paths
    if len(cwd) > 25:
        cwd = "..." + cwd[-22:]

    # Construct the prompt with colors
    prompt = (
        f"{Colors.PROMPT_USER}{user}@{hostname}{Colors.RESET}:"
        f"{Colors.PROMPT_DIR}{cwd}{Colors.RESET}"
        f"{Colors.PROMPT_SYMBOL}$ {Colors.RESET}"
    )
    return prompt

def print_banner():
    """Print a beautiful startup banner."""
    banner = f"""
{Colors.BRIGHT_MAGENTA}╔══════════════════════════════════════════════╗
║                                              ║
║      {Colors.BOLD}Welcome to CustomShell v1.0{Colors.RESET}{Colors.BRIGHT_MAGENTA}         ║
║          {Colors.CYAN}Your Enhanced Terminal Experience{Colors.RESET}{Colors.BRIGHT_MAGENTA}     ║
║                                              ║
╚══════════════════════════════════════════════╝{Colors.RESET}

Type {Colors.YELLOW}'help'{Colors.RESET} for a list of commands or {Colors.YELLOW}'exit'{Colors.RESET} to quit.
"""
    print(banner)

def print_success(message):
    """Print a success message in green."""
    print(f"{Colors.SUCCESS}[+] {message}{Colors.RESET}")

def print_error(message):
    """Print an error message in red."""
    print(f"{Colors.ERROR}[-] {message}{Colors.RESET}")

def print_info(message):
    """Print an informational message in yellow."""
    print(f"{Colors.INFO}[i] {message}{Colors.RESET}")

def strip_ansi_codes(text):
    """Remove ANSI escape codes from a string."""
    # The regex needs to handle the literal \033 that comes from the string
    return re.sub(r'\033\[[0-?]*[ -/]*[@-~]', '', text)
