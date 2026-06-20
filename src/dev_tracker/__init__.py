"""
Dev Tracker
Azure DevOps PR tracking application with multi-project support.
"""

__version__ = "0.1.0"

from dev_tracker.pr_tracker import PRTracker
from dev_tracker.config import ConfigManager

__all__ = ["PRTracker", "ConfigManager", "__version__"]
