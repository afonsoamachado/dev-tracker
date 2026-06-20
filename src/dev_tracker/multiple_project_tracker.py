"""
Multiple Project Tracker module
Orchestrates PR tracking across all configured Azure DevOps projects
"""
from dev_tracker.config import ConfigManager
from dev_tracker.project_tracker import ProjectTracker


class MultipleProjectTracker:
    """Aggregates PR information across all configured projects"""

    def __init__(self):
        self.config_manager = ConfigManager()

    def get_author(self):
        return self.config_manager.get_author()

    def get_all_projects_summary(self):
        """
        Get PR statistics across all configured projects

        Returns:
            dict: Aggregated statistics for all projects
        """
        all_projects = self.config_manager.get_all_projects()
        summary = {
            'all_projects': True,
            'total_projects': len(all_projects),
            'total_repos': 0,
            'total_active': 0,
            'total_completed': 0,
            'total_abandoned': 0,
            'projects': {}
        }

        for project_key, project_config in all_projects.items():
            tracker = ProjectTracker(project_key)
            project_summary = tracker.get_pr_summary()

            summary['total_repos'] += project_summary['total_repos']
            summary['total_active'] += project_summary['total_active']
            summary['total_completed'] += project_summary['total_completed']
            summary['total_abandoned'] += project_summary['total_abandoned']

            summary['projects'][project_key] = {
                'name': project_config.project_name,
                'org': project_config.org,
                'stats': project_summary
            }

        return summary

    def get_all_active_prs(self):
        """
        Get active pull requests across all projects

        Returns:
            dict: Active PRs organized by project
        """
        all_projects = self.config_manager.get_all_projects()
        all_prs = {
            'all_projects': True,
            'projects': {}
        }

        for project_key, project_config in all_projects.items():
            tracker = ProjectTracker(project_key)
            prs = tracker.get_active_prs()

            if prs:
                all_prs['projects'][project_key] = {
                    'name': project_config.project_name,
                    'org': project_config.org,
                    'prs': prs
                }

        return all_prs
