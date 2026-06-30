"""
Project Tracker module
Tracks and processes PR data for a single Azure DevOps project
"""
from dev_tracker.azure_devops.git_client import AzureDevOpsGitClient
from dev_tracker.config import ConfigManager
from dev_tracker.threading_utils import run_parallel


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
        self.client = AzureDevOpsGitClient(project_key)
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
        if not self.project_config.repos:
            return True
        return repo_name in self.project_config.repos

    def _filtered_repos(self, repos, repo_name=None):
        """Return only the repos that pass both the name filter and project filter."""
        return [
            r for r in repos
            if (not repo_name or r['name'] == repo_name)
            and self._should_include_repo(r['name'])
        ]

    def get_author(self):
        return self.config_manager.get_author()

    def get_all_pr_stats(self, force_refresh=False):
        """
        Get PR statistics for all repositories in this project.
        PRs for each repo are fetched in parallel.

        Returns:
            dict: Statistics organized by repository
        """
        repos = self._filtered_repos(self.client.get_repositories(force_refresh=force_refresh))

        def _fetch_repo_stats(repo):
            prs = self.client.get_pull_requests(repo['id'], status='all')
            stats = {
                'repo_name': repo['name'],
                'repo_id': repo['id'],
                'total_prs': len(prs),
                'by_status': {
                    name: sum(1 for pr in prs if pr['status'] == code)
                    for code, name in self.pr_status_map.items()
                }
            }
            return repo['name'], stats

        results = run_parallel(repos, _fetch_repo_stats)
        return dict(results)

    def get_active_prs(self, repo_name=None, force_refresh=False):
        """
        Get active (open) pull requests.
        PRs for each repo are fetched in parallel.

        Args:
            repo_name (str, optional): Filter by specific repository name
            force_refresh (bool): Bypass the repository list cache

        Returns:
            list: List of active PRs with details
        """
        repos = self._filtered_repos(
            self.client.get_repositories(force_refresh=force_refresh),
            repo_name=repo_name,
        )

        def _fetch_repo_prs(repo):
            prs = self.client.get_pull_requests(repo['id'], status='active')
            return [
                {
                    'repo': repo['name'],
                    'pr_id': pr['pullRequestId'],
                    'title': pr['title'],
                    'author': pr['createdBy']['displayName'],
                    'created': pr['creationDate'],
                    'status': self.pr_status_map.get(pr['status'], 'unknown'),
                    'source_branch': pr['sourceRefName'].replace('refs/heads/', ''),
                    'target_branch': pr['targetRefName'].replace('refs/heads/', ''),
                    'url': pr['url'],
                }
                for pr in prs
            ]

        results = run_parallel(repos, _fetch_repo_prs)
        active_prs = []
        for repo_prs in results:
            active_prs.extend(repo_prs)
        return active_prs

    def get_pr_summary(self, repo_name=None, force_refresh=False):
        """
        Get a summary of PR activity.
        PRs for each repo are fetched in parallel.

        Args:
            repo_name (str, optional): Filter by specific repository
            force_refresh (bool): Bypass the repository list cache

        Returns:
            dict: Summary statistics
        """
        repos = self._filtered_repos(
            self.client.get_repositories(force_refresh=force_refresh),
            repo_name=repo_name,
        )

        summary = {
            'project': self.project_config.project_name,
            'organization': self.project_config.org,
            'total_repos': len(repos),
            'total_active': 0,
            'total_completed': 0,
            'total_abandoned': 0,
            'repos': {}
        }

        def _fetch_repo_summary(repo):
            prs = self.client.get_pull_requests(repo['id'], status='all')
            counts = {'active': 0, 'completed': 0, 'abandoned': 0}
            for pr in prs:
                status = self.pr_status_map.get(pr['status'], 'unknown')
                if status in counts:
                    counts[status] += 1
            return repo['name'], counts

        for repo_display_name, counts in run_parallel(repos, _fetch_repo_summary):
            summary['repos'][repo_display_name] = counts
            summary['total_active'] += counts['active']
            summary['total_completed'] += counts['completed']
            summary['total_abandoned'] += counts['abandoned']

        return summary