"""Project common lib"""
import os


def get_available_config():
    """Return all the available config in the config folder"""
    configurations = []
    root_dir = "configurations"
    for path, subdirs, files in os.walk(root_dir):
        for name in files:
            configurations.append(name)
    return configurations
