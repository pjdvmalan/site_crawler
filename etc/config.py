"""
Config module.
"""
from os import path

# The default base URL, required.
TARGER_URL = None
# URL paths to be excluded.
EXCLUDE_PATHS = []
# Report groupings.
DF_GROUP_BY = {}


# Import, parse and validate user's local config in this config file.
try:
    from .config_local import TARGER_URL
except ImportError:
    f_path = path.join(path.dirname(__file__), 'configlocal.py')
    raise ImportError(f"You need to create a local config file at: {f_path}.")

assert TARGER_URL, "Please set the 'target_url' config parameter in 'config_local.py'"
