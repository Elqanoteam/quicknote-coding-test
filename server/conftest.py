"""Configuration for pytest.

This file sets up the Python path so that tests can import from the app module.
"""

import sys
from pathlib import Path

# Add the server directory to Python path so tests can import app modules
server_dir = Path(__file__).parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))
