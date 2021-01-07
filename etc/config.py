"""
Config module.
"""
import os

# Import, parse and validate user's local config in this config file.
try:
    from .config_local import *
except ImportError:
    f_path = os.path.join(os.path.dirname(__file__), 'configlocal.py')
    raise ImportError(f"You need to create a local config file at: {f_path}.")

assert target_url, "Please set the 'target_url' config parameter in 'config_local.py'"
