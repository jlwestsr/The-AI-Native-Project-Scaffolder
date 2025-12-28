"""Git operations for the project generator."""
import sys
import subprocess

def run_command(command, cwd=None):
    """Runs a shell command and handles errors."""
    try:
        subprocess.run(
            command, 
            check=True, 
            shell=True, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        print(f"✔ Executed: {command}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {command}")
        print(e.stderr.decode())
        sys.exit(1)

def init_git(base_path):
    """Initializes Git, commits baseline, and creates develop branch."""
    print("...Initializing Git and Branching Strategy...")
    
    # 1. Init
    run_command("git init", cwd=base_path)
    
    # 2. Add files
    run_command("git add .", cwd=base_path)
    
    # 3. Commit to Main
    run_command('git commit -m "Initial commit: Complete AI project scaffold"', cwd=base_path)
    
    # 4. Create and Switch to Develop branch
    run_command("git checkout -b develop", cwd=base_path)
