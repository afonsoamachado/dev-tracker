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
        
        table = Table(title="Available Projects", show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Project Name", style="green")
        table.add_column("Organization", style="blue")
        table.add_column("Repos", style="yellow")
        
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


def display_summary(project_key=None):
    """Display PR summary for a project or all projects"""
    try:
        if project_key:
            # Show specific project
            tracker = PRTracker(project_key)
            summary = tracker.get_pr_summary()
            
            # Display project header
            header = f"[bold blue]{summary['project']}[/bold blue] (Org: [cyan]{summary['organization']}[/cyan])"
            
            # Display overall stats
            panel_text = f"""
{header}

[cyan]Tracked Repositories:[/cyan] {summary['total_repos']}
[green]Active PRs:[/green] {summary['total_active']}
[yellow]Completed PRs:[/yellow] {summary['total_completed']}
[red]Abandoned PRs:[/red] {summary['total_abandoned']}
            """
            console.print(Panel(panel_text.strip(), expand=False))
            
            # Display per-repo breakdown
            if summary['repos']:
                table = Table(title="Pull Request Status by Repository", show_header=True, header_style="bold magenta")
                table.add_column("Repository", style="cyan")
                table.add_column("Active", justify="right", style="green")
                table.add_column("Completed", justify="right", style="yellow")
                table.add_column("Abandoned", justify="right", style="red")
                
                for repo_name, stats in summary['repos'].items():
                    table.add_row(
                        repo_name,
                        str(stats['active']),
                        str(stats['completed']),
                        str(stats['abandoned'])
                    )
                
                console.print(table)
        else:
            # Show all projects
            tracker = PRTracker()
            all_summary = tracker.get_all_projects_summary()
            
            # Display overall stats
            panel_text = f"""
[bold blue]All Projects Summary[/bold blue]

[cyan]Total Projects:[/cyan] {all_summary['total_projects']}
[cyan]Total Repositories:[/cyan] {all_summary['total_repos']}
[green]Active PRs:[/green] {all_summary['total_active']}
[yellow]Completed PRs:[/yellow] {all_summary['total_completed']}
[red]Abandoned PRs:[/red] {all_summary['total_abandoned']}
            """
            console.print(Panel(panel_text.strip(), expand=False))
            
            # Display per-project breakdown
            if all_summary['projects']:
                table = Table(title="Projects Summary", show_header=True, header_style="bold magenta")
                table.add_column("Project Key", style="cyan")
                table.add_column("Project Name", style="green")
                table.add_column("Organization", style="blue")
                table.add_column("Repos", justify="right", style="yellow")
                table.add_column("Active", justify="right", style="green")
                table.add_column("Completed", justify="right", style="yellow")
                table.add_column("Abandoned", justify="right", style="red")
                
                for project_key, project_info in all_summary['projects'].items():
                    stats = project_info['stats']
                    table.add_row(
                        project_key,
                        project_info['name'],
                        project_info['org'],
                        str(stats['total_repos']),
                        str(stats['total_active']),
                        str(stats['total_completed']),
                        str(stats['total_abandoned'])
                    )
                
                console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error fetching summary: {e}[/red]")


def display_active_prs(project_key=None, repo_name=None):
    """Display all active (open) pull requests"""
    try:
        if project_key:
            # Show specific project's active PRs
            tracker = PRTracker(project_key)
            active_prs = tracker.get_active_prs(repo_name)
            
            if not active_prs:
                console.print("[yellow]No active pull requests found[/yellow]")
                return
            
            title = "Active Pull Requests"
            if repo_name:
                title += f" (Repo: {repo_name})"
            
            table = Table(title=title, show_header=True, header_style="bold magenta")
            table.add_column("Repository", style="cyan")
            table.add_column("PR #", justify="right")
            table.add_column("Title", style="green")
            table.add_column("Author", style="blue")
            table.add_column("Branch", style="yellow")
            
            for pr in active_prs:
                table.add_row(
                    pr['repo'],
                    str(pr['pr_id']),
                    pr['title'][:40],
                    pr['author'],
                    f"{pr['source_branch']} → {pr['target_branch']}"
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
                console.print(f"\n[bold cyan]{project_info['name']}[/bold cyan] (Org: [blue]{project_info['org']}[/blue])")
                
                table = Table(title=f"Active PRs - {project_key}", show_header=True, header_style="bold magenta")
                table.add_column("Repository", style="cyan")
                table.add_column("PR #", justify="right")
                table.add_column("Title", style="green")
                table.add_column("Author", style="blue")
                table.add_column("Branch", style="yellow")
                
                for pr in project_info['prs']:
                    table.add_row(
                        pr['repo'],
                        str(pr['pr_id']),
                        pr['title'][:40],
                        pr['author'],
                        f"{pr['source_branch']} → {pr['target_branch']}"
                    )
                
                console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error fetching active PRs: {e}[/red]")


def display_help():
    """Display help information"""
    help_text = """
[bold cyan]Repo Tracker - Azure DevOps PR Monitor[/bold cyan]
Multi-Project Support - View All Projects Together

[bold]Usage:[/bold]
  python main.py [command] [project_key] [optional_args]

[bold]Commands:[/bold]
  [green]projects[/green]                      - List all configured projects
  [green]summary[/green]                       - Show PR summary for ALL projects (default)
  [green]summary[/green] [PROJECT_1]           - Show PR summary for specific project
  [green]active[/green]                        - Show active PRs across ALL projects
  [green]active[/green] [PROJECT_1]            - Show active PRs in specific project
  [green]active[/green] [PROJECT_1] [repo]     - Show active PRs for specific repo
  [green]help[/green]                          - Display this help message

[bold]Setup:[/bold]
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
    elif command == "summary":
        display_summary(project_key)
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("[yellow]Use 'python main.py help' for usage information[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()
