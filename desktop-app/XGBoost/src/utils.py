# src/utils.py
import os

def ensure_dir(path: str):
    """Create a directory if it does not exist."""
    os.makedirs(path, exist_ok=True)

def print_section(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)