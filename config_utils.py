"""
Configuration utilities for cross-platform settings management
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key


def get_app_config_dir():
    """
    Get the appropriate configuration directory for the application based on the platform.

    Returns:
        Path: Path to the application configuration directory
    """
    if sys.platform == "darwin":  # macOS
        # Use ~/Library/Application Support/AudioTranscription
        config_dir = Path.home() / "Library" / "Application Support" / "AudioTranscription"
    elif sys.platform == "win32":  # Windows
        # Use %APPDATA%/AudioTranscription
        appdata = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        config_dir = Path(appdata) / "AudioTranscription"
    else:  # Linux and others
        # Use ~/.config/AudioTranscription
        config_dir = Path.home() / ".config" / "AudioTranscription"

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir


def get_env_file_path():
    """
    Get the path to the .env file for storing API keys and settings.

    Returns:
        Path: Path to the .env file
    """
    return get_app_config_dir() / "config.env"


def load_api_key():
    """
    Load the Deepgram API key from the configuration file.

    Returns:
        str|None: The API key, or None if not found
    """
    env_file = get_env_file_path()

    # Load the env file if it exists
    if env_file.exists():
        load_dotenv(env_file, override=True)

    return os.getenv("DEEPGRAM_API_KEY")


def save_api_key(api_key):
    """
    Save the Deepgram API key to the configuration file.

    Args:
        api_key (str): The API key to save

    Returns:
        bool: True if successful, False otherwise

    Raises:
        Exception: If there's an error saving the key
    """
    env_file = get_env_file_path()

    # Ensure the directory exists
    env_file.parent.mkdir(parents=True, exist_ok=True)

    # Save the key
    set_key(str(env_file), "DEEPGRAM_API_KEY", api_key)

    # Reload to verify
    load_dotenv(str(env_file), override=True)

    return True
