"""
Multiple Project Tracker module
Orchestrates PR tracking across all configured Azure DevOps projects.
Projects are fetched in parallel (one thread per project).
"""
from dev_tracker.config import ConfigManager
from dev_tracker.project_tracker import ProjectTracker
from dev_tracker.threading_utils import run_parallel


class MultipleProjectTracker:
    """Aggregates PR information across all configured projects"""

    def __init__(self):
        self.config_manager = ConfigManager()

    def get_author(self):
        return self.config_manager.get_author()

    def get_all_projects_summary(self, force_refresh=False):
        """
        Get PR statistics across all configured projects.
        Each project is queried in its own thread.

        Returns:
            dict: Aggregated statistics for all projects
        """
        all_projects = self.config_manager.get_all_projects()

        def _fetch_project_summary(item):
            project_key, project_config = item
            tracker = ProjectTracker(project_key)
            return project_key, project_config, tracker.get_pr_summary(force_refresh=force_refresh)

        summary = {
            'all_projects': True,
            'total_projects': len(all_projects),
            'total_repos': 0,
            'total_active': 0,
            'total_completed': 0,
            'total_abandoned': 0,
            'projects': {}
        }

        results = run_parallel(all_projects.items(), _fetch_project_summary)
        for project_key, project_config, project_summary in results:
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

    def get_all_active_prs(self, force_refresh=False):
        """
        Get active pull requests across all projects.
        Each project is queried in its own thread.

        Returns:
            dict: Active PRs organized by project
        """
        all_projects = self.config_manager.get_all_projects()

        def _fetch_project_prs(item):
            project_key, project_config = item
            tracker = ProjectTracker(project_key)
            return project_key, project_config, tracker.get_active_prs(force_refresh=force_refresh)

        all_prs = {
            'all_projects': True,
            'projects': {}
        }

        results = run_parallel(all_projects.items(), _fetch_project_prs)
        for project_key, project_config, prs in results:
            if prs:
                all_prs['projects'][project_key] = {
                    'name': project_config.project_name,
                    'org': project_config.org,
                    'prs': prs
                }

        return all_prs