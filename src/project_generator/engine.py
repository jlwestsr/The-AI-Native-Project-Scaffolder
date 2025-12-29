"""Core scaffolding engine."""
import os
import sys
from .assets import configs, templates

def check_greenfield(path):
    """Ensures the directory is empty (ignoring the script itself)."""
    # Filter out common files like .git or this tool's files if they exist
    existing_items = [f for f in os.listdir(path) if f not in [".git", "init_project.py"]]
    if existing_items:
        print(f"❌ Error: Directory '{path}' is not empty. Please run this in a greenfield folder.")
        print(f"   Found: {existing_items}")
        sys.exit(1)

def create_structure(base_path, update=False):
    """Creates folders and files.
    
    Args:
        base_path: The root directory for the project.
        update: If True, do not verify directory is empty and do not overwrite existing files.
    """
    print("...Scaffolding folder structure...")
    
    # Create Directories
    for folder in configs.PROJECT_STRUCTURE:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    
    # Create Files
    for filename, content in configs.FILES_TO_CREATE.items():
        file_path = os.path.join(base_path, filename)
        # Ensure directory exists for nested files (like workflows)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if update and os.path.exists(file_path):
            print(f"   [SKIP] {filename} (Exists)")
            continue
            
        with open(file_path, 'w') as f:
            f.write(content.strip())
            
    # Create .gitignore specifically
    with open(os.path.join(base_path, ".gitignore"), 'w') as f:
        f.write(templates.GITIGNORE_CONTENT.strip())
