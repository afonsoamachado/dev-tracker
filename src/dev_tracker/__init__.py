"""
Dev Tracker
Azure DevOps PR tracking application with multi-project support.
"""

__version__ = "0.1.0"

from dev_tracker.project_tracker import ProjectTracker
from dev_tracker.multiple_project_tracker import MultipleProjectTracker
from dev_tracker.config import ConfigManager

__all__ = ["ProjectTracker", "MultipleProjectTracker", "ConfigManager", "__version__"]