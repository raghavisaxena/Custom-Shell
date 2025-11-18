import os
from core_shell import shell_loop
from usability_features import load_aliases
from command_exec import jobs  # Import the jobs list

def main():
    """Initialize and run the custom shell."""
    # Set up environment
    os.environ['SHELL'] = 'customshell'

    # Load aliases
    aliases = load_aliases()

    # Initialize the jobs list (if needed)
    if not isinstance(jobs, list):
        print("Error: Jobs list not properly initialized.", file=os.sys.stderr)
        return

    # Run the shell
    shell_loop(aliases)

if __name__ == "__main__":
    main()