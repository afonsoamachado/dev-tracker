"""
Allows running the package as a module:
    python -m dev_tracker [command] [project_key] [optional_args]
"""
from dev_tracker.cli import main

if __name__ == "__main__":
    main()
