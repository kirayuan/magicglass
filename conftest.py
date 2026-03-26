"""Root conftest – ensures src/ is on the Python path for test discovery."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
