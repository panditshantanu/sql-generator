#!/usr/bin/env python3
"""
Main entry point for SQL Generator CLI.
Use this script to interact with the SQL Generator.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sql_generator.cli import main

if __name__ == "__main__":
    main()
