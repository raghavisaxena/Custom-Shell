# usability_features.py
import os
import readline

class UsabilityFeatures:
    def __init__(self):
        self.history = []
        self.aliases = {}

    def add_history(self, command):
        if command.strip():
            self.history.append(command)
            readline.add_history(command)

    def get_alias(self, cmd):
        return self.aliases.get(cmd, cmd)

    def set_alias(self, alias_name, command):
        self.aliases[alias_name] = command

    def expand_aliases(self, command_line):
        parts = command_line.strip().split()
        if parts and parts[0] in self.aliases:
            aliased_cmd = self.aliases[parts[0]]
            # Replace first word with alias expansion
            new_cmd = aliased_cmd + " " + " ".join(parts[1:])
            return new_cmd.strip()
        return command_line

    def colored_prompt(self):
        user = os.getenv("USER") or "user"
        cwd = os.getcwd()
        # ANSI color codes
        GREEN = "\033[32m"
        BLUE = "\033[34m"
        RESET = "\033[0m"
        return f"{GREEN}{user}{RESET}:{BLUE}{cwd}{RESET} $ "
