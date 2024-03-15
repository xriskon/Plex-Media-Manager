"""Plex Librarian Config Module

This module loads the config.yml file.
"""
import yaml


def load_config():
    """
    Loads the config.yml file
    Returns:
        dict: config, None otherwise
    """
    # Import CLoader
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper
    # Load config.yml
    try:
        config = yaml.load(open("config/config.yml", "r"), Loader=Loader)
    except Exception as e:
        print(f"Couldn't load config.yml\n{e}")
        return None
    return config
