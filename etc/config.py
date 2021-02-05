"""
Config module.
"""
from os import path

# Configure the following in config_local.py
TARGER_URL = None
EXCLUDE_PATHS = []
DF_GROUP_BY = {}


# Import, parse and validate user's local config in this config file.
try:
    # pylint: disable=unused-import
    from .config_local import TARGER_URL, EXCLUDE_PATHS, DF_GROUP_BY
except ImportError:
    f_path = path.join(path.dirname(__file__), 'configlocal.py')
    raise ImportError(f"You need to create a local config file at: {f_path}.")

assert TARGER_URL, "Please set the 'target_url' config parameter in 'config_local.py'"
