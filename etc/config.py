"""
Config module.
"""
from os import path

# Configure the following in config_local.py. See 'config_local_template.py'.
TARGER_URL = None
EXCLUDE_PATHS = []
DF_GROUP_BY = {}
GOOGLE_PS_API_KEY = None

# Import, parse and validate user's local config in this config file.
try:
    # pylint: disable=unused-import
    from .config_local import TARGER_URL, EXCLUDE_PATHS, DF_GROUP_BY, GOOGLE_PS_API_KEY
except ImportError:
    f_path = path.join(path.dirname(__file__), 'configlocal.py')
    raise ImportError(f"You need to create a local config file at: {f_path}.")
