"""CLI Entry point for the project generator."""
import os
import argparse
import sys
from . import engine, git_ops, config_manager


def main():
    parser = argparse.ArgumentParser(
        description="Forge a production-grade AI project structure."
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=os.getcwd(),
        help="Directory to initialize the project in (default: current directory)"
    )
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="Update an existing project (add missing files without overwriting)"
    )
    parser.add_argument(
        "--manager",
        choices=["pip", "poetry", "uv"],
        default=None,
        help="Package manager to use"
    )
    # Global Config Arguments
    parser.add_argument(
        "--config-set",
        nargs="+",
        help="Set global config values (e.g. --config-set author_name='Jane Doe')"
    )
    parser.add_argument(
        "--config-list",
        action="store_true",
        help="List current global configuration"
    )
    args = parser.parse_args()

    # Handle Configuration Commands
    if args.config_list:
        config = config_manager.load_config()
        print(f"Global Config ({config_manager.get_config_path()}):")
        for k, v in config.items():
            print(f"  {k} = {v}")
        return

    if args.config_set:
        for setting in args.config_set:
            if "=" in setting:
                key, value = setting.split("=", 1)
                config_manager.set_setting(key, value)
                print(f"✅ Updated {key} = {value}")
            else:
                print(f"❌ Invalid format: {setting}. Use key=value.")
        return

    target_path = os.path.abspath(args.target_dir)
    context = {}

    # Interactive Mode Check
    # If no target specified (uses default), update flag is strict False, and TTY
    if args.target_dir == os.getcwd() and not args.update and sys.stdin.isatty():
        try:
            from . import wizard
            context = wizard.run_wizard()
        except ImportError:
            print("Warning: fit/questionary not found. Skipping interactive mode.")

    print(f"Starting AI Project Initialization in: {target_path}")

    # Ensure directory exists
    os.makedirs(target_path, exist_ok=True)

    # 1. Safety Check (skip if updating)
    if not args.update:
        engine.check_greenfield(target_path)

    # 2. Build Structure
    if args.manager:
        context["__PACKAGE_MANAGER__"] = args.manager

    engine.create_structure(target_path, update=args.update, context=context)

    # 3. Git Operations
    if not os.path.exists(os.path.join(target_path, ".git")):
        git_ops.init_git(target_path)
    else:
        print("...Skipping Git Init (Already initialized)...")

    print("\n✅ Success! Project is ready.")
    print("   - You are currently on the 'develop' branch.")
    print("   - CI/CD is configured in .github/workflows/unittests.yml")
    print("   - Linter/Formatter configs are set (.flake8, pyproject.toml)")
    print("   - Aider context is ready in CONTEXT.md")
    print("   - AI behavior rules are ready in rules/ai_behavior.md")
    print("   - Feature documentation structure is ready in docs/")


if __name__ == "__main__":
    main()
