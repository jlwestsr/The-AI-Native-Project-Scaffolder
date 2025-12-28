"""CLI Entry point for the project generator."""
import os
import argparse
from . import engine, git_ops

def main():
    parser = argparse.ArgumentParser(description="Forge a production-grade AI project structure.")
    parser.add_argument(
        "target_dir", 
        nargs="?", 
        default=os.getcwd(), 
        help="Directory to initialize the project in (default: current directory)"
    )
    args = parser.parse_args()

    target_path = os.path.abspath(args.target_dir)
    
    print(f"Starting AI Project Initialization in: {target_path}")
    
    # Ensure directory exists
    os.makedirs(target_path, exist_ok=True)
    
    # 1. Safety Check
    engine.check_greenfield(target_path)
    
    # 2. Build Structure
    engine.create_structure(target_path)
    
    # 3. Git Operations
    git_ops.init_git(target_path)
    
    print("\n✅ Success! Project is ready.")
    print("   - You are currently on the 'develop' branch.")
    print("   - CI/CD is configured in .github/workflows/unittests.yml")
    print("   - Linter/Formatter configs are set (.flake8, pyproject.toml)")
    print("   - Aider context is ready in CONTEXT.md")
    print("   - AI behavior rules are ready in rules/ai_behavior.md")
    print("   - Feature documentation structure is ready in docs/")

if __name__ == "__main__":
    main()
