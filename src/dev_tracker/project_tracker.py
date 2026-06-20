"""
Project Tracker module
Tracks and processes PR data for a single Azure DevOps project
"""
from dev_tracker.api_client import AzureDevOpsClient
from dev_tracker.config import ConfigManager


class ProjectTracker:
    """Tracks and manages pull request information for one project"""

    def __init__(self, project_key):
        """
        Initialize the PR tracker for a specific project

        Args:
            project_key (str): Project key like "PROJECT_1"
        """
        self.project_key = project_key
        self.config_manager = ConfigManager()
        self.client = AzureDevOpsClient(project_key)
        self.project_config = self.config_manager.get_project(project_key)

        self.pr_status_map = {
            1: "active",
            2: "abandoned",
            3: "completed"
        }

    def _should_include_repo(self, repo_name):
        """
        Check if a repo should be included based on filter

        Args:
            repo_name (str): Repository name

        Returns:
            bool: True if repo should be included
        """
        # If repo_filter is empty, include all repos
        if not self.project_config.repos:
            return True
        # Otherwise, only include repos in the filter list
        return repo_name in self.project_config.repos

    def get_author(self):
        return self.config_manager.get_author()

    def get_all_pr_stats(self):
        """
        Get PR statistics for all repositories in this project

        Returns:
            dict: Statistics organized by repository
        """
        repos = self.client.get_repositories()
        all_stats = {}

        for repo in repos:
            repo_name = repo['name']

            # Skip repos not in filter list
            if not self._should_include_repo(repo_name):
                continue

            repo_id = repo['id']

            # Get all PRs (active + completed + abandoned)
            prs = self.client.get_pull_requests(repo_id, status='all')

            stats = {
                'repo_name': repo_name,
                'repo_id': repo_id,
                'total_prs': len(prs),
                'by_status': {}
            }

            # Count by status
            for status_code, status_name in self.pr_status_map.items():
                status_prs = [pr for pr in prs if pr['status'] == status_code]
                stats['by_status'][status_name] = len(status_prs)

            all_stats[repo_name] = stats

        return all_stats

    def get_active_prs(self, repo_name=None):
        """
        Get active (open) pull requests

        Args:
            repo_name (str, optional): Filter by specific repository name

        Returns:
            list: List of active PRs with details
        """
        repos = self.client.get_repositories()
        active_prs = []

        for repo in repos:
            repo_display_name = repo['name']

            # Skip if doesn't match specific repo filter or project repo filter
            if repo_name and repo_display_name != repo_name:
                continue
            if not self._should_include_repo(repo_display_name):
                continue

            prs = self.client.get_pull_requests(repo['id'], status='active')

            for pr in prs:
                active_prs.append({
                    'repo': repo_display_name,
                    'pr_id': pr['pullRequestId'],
                    'title': pr['title'],
                    'author': pr['createdBy']['displayName'],
                    'created': pr['creationDate'],
                    'status': self.pr_status_map.get(pr['status'], 'unknown'),
                    'source_branch': pr['sourceRefName'].replace('refs/heads/', ''),
                    'target_branch': pr['targetRefName'].replace('refs/heads/', ''),
                    'url': pr['url']
                })

        return active_prs

    def get_pr_summary(self, repo_name=None):
        """
        Get a summary of PR activity

        Args:
            repo_name (str, optional): Filter by specific repository

        Returns:
            dict: Summary statistics
        """
        repos = self.client.get_repositories()
        summary = {
            'project': self.project_config.project_name,
            'organization': self.project_config.org,
            'total_repos': 0,
            'total_active': 0,
            'total_completed': 0,
            'total_abandoned': 0,
            'repos': {}
        }

        for repo in repos:
            repo_display_name = repo['name']

            # Skip if doesn't match specific repo filter or project repo filter
            if repo_name and repo_display_name != repo_name:
                continue
            if not self._should_include_repo(repo_display_name):
                continue

            summary['total_repos'] += 1
            prs = self.client.get_pull_requests(repo['id'], status='all')

            repo_summary = {
                'active': 0,
                'completed': 0,
                'abandoned': 0
            }

            for pr in prs:
                status = self.pr_status_map.get(pr['status'], 'unknown')
                if status == 'active':
                    repo_summary['active'] += 1
                    summary['total_active'] += 1
                elif status == 'completed':
                    repo_summary['completed'] += 1
                    summary['total_completed'] += 1
                elif status == 'abandoned':
                    repo_summary['abandoned'] += 1
                    summary['total_abandoned'] += 1

            summary['repos'][repo_display_name] = repo_summary

        return summary