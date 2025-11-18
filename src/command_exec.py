import os
from ui import print_error, print_success, print_info

# --- Global Job Management ---
jobs = []

def run_command(command, args, background=False):
    """Run external command with fork/execvp and job control, returning the exit status."""
    full_args = [command] + args
    try:
        pid = os.fork()
        if pid == 0:
            # Child process: Exec the command
            os.execvp(command, full_args)
            # This part is only reached if execvp fails
            os._exit(1)
        else:
            # Parent process: Handle job control
            if not background:
                # Foreground process: Wait for it to complete
                _, status = os.waitpid(pid, 0)
                if os.WIFEXITED(status):
                    exit_code = os.WEXITSTATUS(status)
                    if exit_code == 0:
                        print_success(f"Command '{command}' completed.")
                    else:
                        print_error(f"Command '{command}' failed with exit code {exit_code}.")
                    return exit_code
                else:
                    print_error(f"Command '{command}' terminated abnormally.")
                    return -1
            else:
                # Background process: Add to jobs list and return immediately
                jobs.append({'pid': pid, 'command': ' '.join(full_args), 'status': 'Running'})
                print_info(f"Command '{command}' running in background (PID: {pid}).")
                return 0  # Success
    except FileNotFoundError:
        print_error(f"Command '{command}' not found. Check PATH.")
        return 127
    except PermissionError:
        print_error("Permission denied for command.")
        return 126
    except Exception as e:
        print_error(f"Execution error: {str(e)}")
        return 1

def get_jobs():
    """Return the list of background jobs."""
    # Update job statuses before returning
    for job in jobs:
        # Check if the process is still running
        pid, status = os.waitpid(job['pid'], os.WNOHANG)
        if pid != 0:
            # Process has finished
            job['status'] = 'Done'
    return jobs
