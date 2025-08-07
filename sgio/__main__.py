import sys
import os

def main():
    """Main entry point for the sgio command-line interface."""
    # Get the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (where sgio package is)
    parent_dir = os.path.dirname(current_dir)
    # Add to sys.path if not already there
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from sgio.app import cli
    cli(*sys.argv)

if __name__ == "__main__":
    main()
