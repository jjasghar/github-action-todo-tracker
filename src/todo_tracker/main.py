#!/usr/bin/env python3
"""
Main entry point for the TODO Tracker application.

This module provides the main entry point that can be used both as a standalone
CLI application and as a GitHub Action.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from todo_tracker.cli import cli


def main() -> None:
    """Main entry point for the application."""
    cli()


if __name__ == '__main__':
    main()
