"""
Shared pytest fixtures for all tests.
Add the src directory to the path so tests can import application modules.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent))
