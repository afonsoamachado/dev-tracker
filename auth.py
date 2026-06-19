"""
Azure DevOps authentication module
Handles PAT-based authentication for Azure DevOps API
"""
import os
import base64
from config import ConfigManager


class AzureDevOpsAuth:
    """Handles authentication with Azure DevOps"""
    
    def __init__(self, project_key=None):
        """
        Initialize authentication for a specific project
        
        Args:
            project_key (str, optional): Project key like "PROJECT_1" 
                                       If None, uses default project
        """
        config_manager = ConfigManager()
        
        if project_key:
            project_config = config_manager.get_project(project_key)
        else:
            project_config = config_manager.get_default_project()
        
        self.project_key = project_config.project_key
        self.organization = project_config.org
        self.personal_access_token = project_config.pat
        self.project = project_config.project_name
        self.repo_filter = project_config.repos
        
        if not all([self.organization, self.personal_access_token, self.project]):
            raise ValueError(
                f"Missing required configuration for {self.project_key}. "
                "Please check your .env file."
            )
    
    def get_auth_header(self):
        """
        Generate Basic Authentication header for Azure DevOps API
        
        Returns:
            dict: Authorization header
        """
        # Azure DevOps uses Basic auth with PAT as password
        # Username is empty, password is the PAT
        credentials = f":{self.personal_access_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
    
    def get_base_url(self):
        """
        Get the base URL for Azure DevOps API
        
        Returns:
            str: Base URL
        """
        return f"https://dev.azure.com/{self.organization}"
