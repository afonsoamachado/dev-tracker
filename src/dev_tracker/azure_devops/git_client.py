"""
Azure DevOps API client module
Handles all HTTP requests to the Azure DevOps REST API
"""
import requests
from dev_tracker.azure_devops.auth import AzureDevOpsAuth


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
    
    def get_repositories(self):
        """
        Get all repositories in the project
        
        Returns:
            list: List of repository data
        """
        endpoint = f"_apis/git/repositories?project={self.auth.project}&api-version={self.api_version}"
        response = self._make_request(endpoint)
        return response.get('value', [])
    
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