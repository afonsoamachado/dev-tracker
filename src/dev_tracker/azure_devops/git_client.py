"""
Azure DevOps API client module
Handles all HTTP requests to the Azure DevOps REST API
"""
import hashlib
import json
import os
import requests
from dev_tracker.azure_devops.auth import AzureDevOpsAuth

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
_CACHE_FILE = os.path.join(_CACHE_DIR, "repositories.json")


def _load_repo_cache() -> dict:
    """Load the on-disk repo cache, returning an empty dict on any error."""
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_repo_cache(cache: dict) -> None:
    """Persist the repo cache to disk."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def _repo_filter_fingerprint(repo_filter: list[str]) -> str:
    """
    Return a short hash that represents the current repo filter list.
    When the configured repos change the fingerprint changes, which
    triggers a cache refresh for that project.
    """
    canonical = ",".join(sorted(repo_filter))
    return hashlib.md5(canonical.encode()).hexdigest()[:8]


class AzureDevOpsGitClient:
    """Client for interacting with Azure DevOps REST API"""
    
    def __init__(self, project_key=None):
        """
        Initialize the API client for a specific project
        
        Args:
            project_key (str, optional): Project key like "PROJECT_1"
                                       If None, uses default project
        """
        self.auth = AzureDevOpsAuth(project_key)
        self.base_url = self.auth.get_base_url()
        self.headers = self.auth.get_auth_header()
        self.headers['Content-Type'] = 'application/json'
        self.api_version = "7.0"
        # Unique cache key: org + project name + repo-filter fingerprint
        self._cache_key = (
            f"{self.auth.organization}::{self.auth.project}"
            f"::{_repo_filter_fingerprint(self.auth.repo_filter)}"
        )
    
    def _make_request(self, endpoint, method="GET", params=None):
        """
        Make HTTP request to Azure DevOps API
        
        Args:
            endpoint (str): API endpoint
            method (str): HTTP method (GET, POST, etc.)
            params (dict): Query parameters
            
        Returns:
            dict: JSON response data
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            else:
                response = requests.request(method, url, headers=self.headers, params=params)
            
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request Error: {e}")
    
    def get_repositories(self, force_refresh=False):
        """
        Get all repositories in the project.

        Results are cached in ``<package>/.cache/repositories.json`` and keyed
        by organisation + project + repo-filter fingerprint.  The cache is
        automatically invalidated whenever the configured repo list in .env
        changes.  Pass ``force_refresh=True`` to bypass the cache entirely
        (e.g. after adding a brand-new repo to Azure DevOps).

        Args:
            force_refresh (bool): Skip cache and fetch fresh data from the API.

        Returns:
            list: List of repository data
        """
        if not force_refresh:
            cache = _load_repo_cache()
            if self._cache_key in cache:
                return cache[self._cache_key]

        # Cache miss – fetch from the API and persist
        endpoint = f"_apis/git/repositories?project={self.auth.project}&api-version={self.api_version}"
        response = self._make_request(endpoint)
        repos = response.get('value', [])

        cache = _load_repo_cache()
        cache[self._cache_key] = repos
        _save_repo_cache(cache)

        return repos
    
    def get_pull_requests(self, repo_id, status="active"):
        """
        Get pull requests for a specific repository
        
        Args:
            repo_id (str): Repository ID
            status (str): PR status filter ('active', 'abandoned', 'completed', 'all')
            
        Returns:
            list: List of pull request data
        """
        status_map = {
            'active': 1,
            'abandoned': 2,
            'completed': 3,
            'all': 0
        }
        
        status_code = status_map.get(status, 0)
        endpoint = (
            f"_apis/git/repositories/{repo_id}/pullrequests?"
            f"project={self.auth.project}"
            f"&searchCriteria.status={status_code if status_code else ''}"
            f"&api-version={self.api_version}"
        )
        
        response = self._make_request(endpoint)
        return response.get('value', [])
    
    def get_pull_request_details(self, repo_id, pr_id):
        """
        Get detailed information for a specific pull request
        
        Args:
            repo_id (str): Repository ID
            pr_id (int): Pull request ID
            
        Returns:
            dict: Pull request details
        """
        endpoint = (
            f"_apis/git/repositories/{repo_id}/pullrequests/{pr_id}?"
            f"project={self.auth.project}"
            f"&api-version={self.api_version}"
        )
        
        return self._make_request(endpoint)
    
    def get_pr_threads(self, repo_id, pr_id):
        """
        Get comments/threads for a pull request
        
        Args:
            repo_id (str): Repository ID
            pr_id (int): Pull request ID
            
        Returns:
            list: List of threads/comments
        """
        endpoint = (
            f"_apis/git/repositories/{repo_id}/pullrequests/{pr_id}/threads?"
            f"project={self.auth.project}"
            f"&api-version={self.api_version}"
        )
        
        response = self._make_request(endpoint)
        return response.get('value', [])