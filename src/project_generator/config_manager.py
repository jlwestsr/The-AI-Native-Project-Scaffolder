"""Global Configuration Manager."""
import os
import tomli
import tomli_w
import platformdirs
from pathlib import Path

APP_NAME = "forge"
APP_AUTHOR = "WestAILabs"

def get_config_path():
    """Returns the path to the config file."""
    config_dir = platformdirs.user_config_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(config_dir, exist_ok=True)
    return Path(config_dir) / "config.toml"

def load_config():
    """Loads the configuration from file."""
    path = get_config_path()
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomli.load(f)

def save_config(config):
    """Saves the configuration to file."""
    path = get_config_path()
    with open(path, "wb") as f:
        tomli_w.dump(config, f)

def get_setting(key, default=None):
    """Retrieves a specific setting."""
    config = load_config()
    return config.get(key, default)

def set_setting(key, value):
    """Sets a specific setting."""
    config = load_config()
    config[key] = value
    save_config(config)
