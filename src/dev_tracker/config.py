"""
Configuration manager for multi-project support
Handles loading and managing multiple Azure DevOps projects
"""
import os
from dotenv import load_dotenv


class ProjectConfig:
    """Configuration for a single Azure DevOps project"""
    
    def __init__(self, project_key, org, pat, project_name, repos=None):
        self.project_key = project_key  # e.g., "PROJECT_1"
        self.org = org
        self.pat = pat
        self.project_name = project_name
        self.repos = repos or []
    
    def __repr__(self):
        return f"ProjectConfig({self.project_key}: {self.org}/{self.project_name})"


class ConfigManager:
    """Manages configuration for multiple Azure DevOps projects"""
    
    def __init__(self):
        """Initialize configuration manager"""
        load_dotenv()
        self.org = os.getenv('AZURE_DEVOPS_ORG')
        self.pat = os.getenv('AZURE_DEVOPS_PAT')
        
        if not self.org or not self.pat:
            raise ValueError(
                "Missing required environment variables. "
                "Please set AZURE_DEVOPS_ORG and AZURE_DEVOPS_PAT in your .env file"
            )
        
        self.projects = {}
        self.author = ""
        self._load_projects()
        self._load_author()
    
    def _load_author(self):
        """Load Author Name"""
        candidate = os.getenv('AUTHOR')
        if not candidate:
            return        
        self.author = candidate
        
    def get_author(self):
        """
        Get author configuration
        
        Returns:
            dict: Dictionary of all projects
        """
        return self.author
        
    def _load_projects(self):
        """Load all project configurations from environment variables"""
        project_num = 1
        while True:
            project_key = f"PROJECT_{project_num}"
            project_name = os.getenv(f"{project_key}_NAME")
            repos_str = os.getenv(f"{project_key}_REPOS", "")
            
            if not project_name:
                break
            
            # Parse repos list
            if repos_str.lower() == "all":
                repos = []  # Empty list means all repos
            else:
                repos = [r.strip() for r in repos_str.split(",") if r.strip()]
            
            config = ProjectConfig(
                project_key=project_key,
                org=self.org,
                pat=self.pat,
                project_name=project_name,
                repos=repos
            )
            
            self.projects[project_key] = config
            project_num += 1
        
        if not self.projects:
            raise ValueError(
                "No projects configured. Please add PROJECT_1_NAME and PROJECT_1_REPOS "
                "to your .env file"
            )
    
    def get_project(self, project_key):
        """
        Get a specific project configuration
        
        Args:
            project_key (str): Project key like "PROJECT_1"
            
        Returns:
            ProjectConfig: Project configuration
        """
        if project_key not in self.projects:
            raise ValueError(f"Project '{project_key}' not found")
        return self.projects[project_key]
    
    def get_all_projects(self):
        """
        Get all project configurations
        
        Returns:
            dict: Dictionary of all projects
        """
        return self.projects
    
    def list_projects(self):
        """
        Get a list of all available projects
        
        Returns:
            list: List of project keys and their display names
        """
        return [
            {
                'key': key,
                'name': config.project_name,
                'org': config.org,
                'repos': len(config.repos) if config.repos else 'all'
            }
            for key, config in self.projects.items()
        ]
    
    def get_default_project(self):
        """
        Get the first configured project
        
        Returns:
            ProjectConfig: First project configuration
        """
        if not self.projects:
            raise ValueError("No projects configured")
        # Return the first project in order
        return next(iter(self.projects.values()))
    
    def get_repos_for_project(self, project_key):
        """
        Get repository list for a project
        
        Args:
            project_key (str): Project key
            
        Returns:
            list: List of repo names (empty list means all repos)
        """
        project = self.get_project(project_key)
        return project.repos
