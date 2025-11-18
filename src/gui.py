import tkinter as tk
from tkinter import scrolledtext, END
import os
import sys
import shlex
import glob
from queue import Queue
import threading

# Import core logic and UI components
from core_shell import handle_builtin
from command_exec import run_command
from usability_features import load_aliases, save_aliases, expand_alias, COMMANDS
from ui import strip_ansi_codes, get_colored_prompt

class GuiOutput:
    """A file-like object to redirect stdout to the GUI text area."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = Queue()
        self.text_widget.after(100, self.process_queue)

    def write(self, s):
        # Strip ANSI codes and put the clean string into the queue
        clean_s = strip_ansi_codes(s)
        self.queue.put(clean_s)

    def process_queue(self):
        """Process the queue to update the GUI from the main thread."""
        while not self.queue.empty():
            s = self.queue.get_nowait()
            self.text_widget.config(state=tk.NORMAL)
            if s.startswith("[+]"):
                tag = "success"
            elif s.startswith("[-]"):
                tag = "error"
            elif s.startswith("[i]"):
                tag = "info"
            else:
                tag = "output"
            self.text_widget.insert(END, s, tag)
            self.text_widget.config(state=tk.DISABLED)
            self.text_widget.see(END)
        self.text_widget.after(100, self.process_queue)

    def flush(self):
        pass  # Required for file-like objects

class CustomShellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CustomShell v1.0 - GUI")
        self.root.geometry("800x600")
        self.root.configure(bg='#212121')

        self.tag_colors = {
            'success': '#4CAF50', 
            'error': '#F44336',   
            'info': '#FFC107',    
            'prompt': '#2196F3',  
            'command': '#E0E0E0', 
            'output': '#FFFFFF'  
        }

        self.aliases = load_aliases()
        self.history = []
        self.current_history_index = 0
        self.last_completion_text = None
        self.completion_options = []
        self.completion_index = 0

        self.setup_ui()
        self.configure_tags()
        self.update_prompt()

        self.gui_output = GuiOutput(self.output_text)
        sys.stdout = self.gui_output
        sys.stderr = self.gui_output

        self.print_banner_gui()

    def setup_ui(self):
        self.output_text = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, bg='#212121', fg='white',
            font=('Segoe UI', 11), state=tk.DISABLED, relief=tk.FLAT
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(self.root, bg='#212121')
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.prompt_label = tk.Label(input_frame, font=('Segoe UI', 11, 'bold'), bg='#212121')
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            input_frame, bg='#333', fg='white', insertbackground='white',
            font=('Segoe UI', 11), relief=tk.FLAT
        )
        self.input_entry.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=5)
        self.input_entry.bind('<Return>', self.process_command_gui)
        self.input_entry.bind('<Up>', self.history_up)
        self.input_entry.bind('<Down>', self.history_down)
        self.input_entry.bind('<Tab>', self.handle_autocomplete)
        self.input_entry.bind('<Key>', self.reset_autocomplete)
        self.input_entry.focus()

    def configure_tags(self):
        for tag, color in self.tag_colors.items():
            self.output_text.tag_config(tag, foreground=color)

    def print_banner_gui(self):
        banner = """
Welcome to CustomShell v1.0
Type 'help' to see a list of commands, or 'exit' to quit.
"""
        print(banner)

    def update_prompt(self):
        prompt_text = strip_ansi_codes(get_colored_prompt())
        self.prompt_label.config(text=prompt_text, fg=self.tag_colors['prompt'])
        return prompt_text
    
    def echo_command(self, prompt, command):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(END, prompt, "prompt")
        self.output_text.insert(END, command + '\n', "command")
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(END)

    def process_command_gui(self, event=None):
        inp = self.input_entry.get().strip()
        if not inp:
            return

        prompt_text = self.update_prompt()
        self.echo_command(prompt_text, inp)
        
        if inp not in self.history:
            self.history.append(inp)
        self.current_history_index = len(self.history)
        self.input_entry.delete(0, END)
        self.reset_autocomplete()

        threading.Thread(target=self.execute_in_thread, args=(inp,), daemon=True).start()

    def execute_in_thread(self, inp):
        try:
            inp = expand_alias(inp, self.aliases)
            background = inp.endswith('&')
            if background:
                inp = inp[:-1].strip()

            args = shlex.split(inp)
            if not args: return
            
            expanded_args = []
            for arg in args[1:]:
                if any(c in arg for c in '*?['):
                    glob_matches = glob.glob(arg)
                    if glob_matches:
                        expanded_args.extend(glob_matches)
                    else:
                        expanded_args.append(arg)
                else:
                    expanded_args.append(arg)
            
            command = args[0]
            args = expanded_args

            if command == 'exit':
                self.root.quit()
                return
            if command == 'cd':
                handle_builtin(command, args, self.aliases)
                self.root.after(0, self.update_prompt)
                return

            if handle_builtin(command, args, self.aliases):
                pass
            else:
                run_command(command, args, background)

        except Exception as e:
            print(f"[-] GUI Execution Error: {e}")

    def reset_autocomplete(self, event=None):
        if event and event.keysym == 'Tab': return
        self.last_completion_text = None
        self.completion_options = []
        self.completion_index = 0

    def handle_autocomplete(self, event):
        current_text = self.input_entry.get()
        if current_text != self.last_completion_text:
            self.reset_autocomplete()
            self.last_completion_text = current_text
            
            if ' ' not in current_text:
                self.completion_options = [cmd for cmd in COMMANDS if cmd.startswith(current_text)]
            else:
                self.completion_options = [p for p in glob.glob(current_text + '*')]

        if self.completion_options:
            if self.completion_index >= len(self.completion_options):
                self.completion_index = 0
            
            completion = self.completion_options[self.completion_index]
            self.input_entry.delete(0, END)
            self.input_entry.insert(0, completion)
            
            self.completion_index += 1
        
        return 'break' # Prevents default Tab behavior

    def history_up(self, event):
        if self.history and self.current_history_index > 0:
            self.current_history_index -= 1
            self.input_entry.delete(0, END)
            self.input_entry.insert(0, self.history[self.current_history_index])
        return 'break'

    def history_down(self, event):
        if self.history and self.current_history_index < len(self.history):
            if self.current_history_index < len(self.history) - 1:
                self.current_history_index += 1
                self.input_entry.delete(0, END)
                self.input_entry.insert(0, self.history[self.current_history_index])
            else:
                self.current_history_index += 1
                self.input_entry.delete(0, END)
        return 'break'

    def on_close(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomShellGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
