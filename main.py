"""
Repo Tracker CLI
Main entry point for the Azure DevOps PR tracking application
Multi-project support with repo selection
"""
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from pr_tracker import PRTracker
from config import ConfigManager


console = Console()

def display_projects():
    """Display all configured projects"""
    try:
        config_manager = ConfigManager()
        projects = config_manager.list_projects()
        
        if not projects:
            console.print("[yellow]No projects configured[/yellow]")
            return
        
        table = _create_table("Available Projects")
        _add_column(table, "Key")
        _add_column(table, "Project Name")
        _add_column(table, "Organization")
        _add_column(table, "Repos")
        
        for project in projects:
            table.add_row(
                project['key'],
                project['name'],
                project['org'],
                str(project['repos'])
            )
        
        console.print(table)
        console.print("\n[dim]Use: python main.py summary PROJECT_1 (for specific project)[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error listing projects: {e}[/red]")


def display_active_prs(project_key=None, repo_name=None):
    """Display all active (open) pull requests"""
    try:
        if project_key and repo_name:
            # Show specific project's active PRs
            tracker = PRTracker(project_key)
            active_prs = tracker.get_active_prs(repo_name)
            
            if not active_prs:
                console.print("[yellow]No active pull requests found[/yellow]")
                return
            
            title = "Active Pull Requests"
            if repo_name:
                title += f" (Repo: {repo_name})"

            table = _create_table(title)
            _add_column(table, "Repository")
            _add_column(table, "PR #", justify="right")
            _add_column(table, "Title")
            _add_column(table, "Author")
            _add_column(table, "Branch")
            
            
            for pr in sorted(active_prs, key=lambda x: x['author']):
                author_style = "bold yellow" if pr['author'] == tracker.get_author() else "white"
                table.add_row(
                    _add_pr_row(table,pr,author_style)
                )
            
            console.print(table)
        else:
            # Show all projects' active PRs
            tracker = PRTracker()
            all_prs = tracker.get_all_active_prs()
            
            if not all_prs['projects']:
                console.print("[yellow]No active pull requests found in any project[/yellow]")
                return
            
            for project_key, project_info in all_prs['projects'].items():   
                title = f"\n[bold blue]{project_info['name']}[/bold blue] (Org: [white]{project_info['org']}[/white])"              
                table = _create_table(title)
                _add_column(table, "Repository")
                _add_column(table, "PR #", justify="right")
                _add_column(table, "Title")
                _add_column(table, "Author")
                _add_column(table, "Branch")
                
                for pr in sorted(project_info['prs'], key=lambda x: x['author']):
                    author_style = "bold yellow" if pr['author'] == tracker.get_author() else "white"
                    _add_pr_row(table,pr,author_style)
                
                console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error fetching active PRs: {e}[/red]")

def _add_pr_row(table,pr,style):
    return table.add_row(
        f"[{style}]{pr['repo']}[/{style}]",
        f"[{style}]{str(pr['pr_id'])}[/{style}]",
        f"[{style}]{pr['title'][:40]}[/{style}]",
        f"[{style}]{pr['author']}[/{style}]",
        f"[{style}]{pr['source_branch']} → {pr['target_branch']}[/{style}]"
    )

def _create_table(table_title):
    return Table(title=table_title, show_header=True, header_style="bold blue", show_lines=True)

def _add_column(table,col_title, justify="left"):
    return table.add_column(col_title, style="white",justify=justify, overflow="fold", no_wrap=False)

def display_help():
    """Display help information"""
    help_text = """
    [bold cyan]Repo Tracker - Azure DevOps PR Monitor[/bold cyan]
    Multi-Project Support - View All Projects Together

    [bold]Usage:[/bold]
    python main.py [command] [project_key] [optional_args]

    [bold]Commands:[/bold]
    [green]projects[/green]                      - List all configured projects
    [green]active[/green]                        - Show active PRs across ALL projects
    [green]active[/green] [PROJECT_1]            - Show active PRs in specific project
    [green]active[/green] [PROJECT_1] [repo]     - Show active PRs for specific repo
    [green]help[/green]                          - Display this help message

    [bold]Notes:[/bold]
    1. Copy .env.example to .env
    2. Add your projects to .env:
        AZURE_DEVOPS_ORG=organization
        AZURE_DEVOPS_PAT=personal-access-token
        PROJECT_1_NAME=project1
        PROJECT_1_REPOS=repo1,repo2,repo3

    3. Add more projects if needed (PROJECT_2, PROJECT_3, etc.)
    """
    console.print(Panel(help_text.strip(), expand=False))


def main():
    """Main entry point"""
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "summary"
    project_key = sys.argv[2] if len(sys.argv) > 2 else None
    optional_arg = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Convert "all" to None (meaning all projects)
    if project_key and project_key.lower() == "all":
        project_key = None
    
    if command == "help":
        display_help()
    elif command == "projects":
        display_projects()
    elif command == "active":
        display_active_prs(project_key, optional_arg)
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("[yellow]Use 'python main.py help' for usage information[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()
