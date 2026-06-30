# Dev Tracker

A cross-platform CLI tool built in Python to monitor your Azure DevOps Pull Requests across multiple projects.
 
> 🤖 This project was developed in collaboration with [Claude](https://claude.ai), used throughout for design decisions, implementation, and documentation — a real-world example of AI-assisted software development.

## 📑 Table of Contents

- [Quick Start](#-quick-start)
- [Commands](#-commands)
- [Repo Cache](#-repo-cache)
- [Project Structure](#-project-structure)
- [Dev Setup](#-dev-setup)

## 🚀 Quick Start

**1. Create your `.env` file:**
```bash
cp .env.example .env
```

**2. Fill in your Azure DevOps details in `.env`:**
```env
AZURE_DEVOPS_ORG=your-organization-name
AZURE_DEVOPS_PAT=your-personal-access-token
AUTHOR=your-display-name

PROJECT_1_NAME=project1
PROJECT_1_REPOS=repo1,repo2,repo3

# Optional: add more projects
PROJECT_2_NAME=project2
PROJECT_2_REPOS=all
```

**3. Run:**
```bash
dev-tracker <command>
```

---

## 📋 Commands

| Command | Description |
|---|---|
| `dev-tracker projects` | List all configured projects |
| `dev-tracker active` | Show active PRs across **all** projects |
| `dev-tracker active PROJECT_1` | Show active PRs for a specific project |
| `dev-tracker active PROJECT_1 my-repo` | Show active PRs for a specific repo |
| `dev-tracker help` | Show help |

### Flags

| Flag | Description |
|---|---|
| `--refresh` | Bypass the local repo cache and fetch fresh data from Azure DevOps |

---

## ⚡ Repo Cache

Repository lists are cached locally per project/org in `dev_tracker/azure_devops/.cache/` to avoid redundant API calls on every run.

The cache is **automatically invalidated** when you change `PROJECT_*_REPOS` in your `.env`. Use `--refresh` to force a fresh fetch if you've added new repos directly in Azure DevOps:

```bash
dev-tracker active --refresh
dev-tracker active PROJECT_1 --refresh
```

PR and repo fetches across projects and repos run in parallel (see `threading_utils.py`), so cache reads/writes are thread-safe by design.

---

## 📁 Project Structure

```
src/
└── dev_tracker/
    ├── azure_devops/
    │   ├── auth.py               # PAT-based authentication for Azure DevOps API
    │   ├── git_client.py         # HTTP client wrapping the Azure DevOps REST API
    │   └── local_repo_cache.py   # Thread-safe on-disk cache for repo lists
    ├── __init__.py                # Package entry point / exports
    ├── __main__.py                # Enables `python -m dev_tracker`
    ├── cli.py                     # CLI command parsing and console output
    ├── config.py                  # Loads and validates .env project configuration
    ├── multiple_project_tracker.py  # Aggregates PR data across all projects (parallel)
    ├── project_tracker.py         # Fetches and summarizes PR data for one project (parallel)
    └── threading_utils.py         # Shared ThreadPoolExecutor helper (run_parallel)
```

| Module | Responsibility |
|---|---|
| `auth.py` | Builds the Basic Auth header from your PAT and resolves project config |
| `git_client.py` | Talks to the Azure DevOps REST API; caches repo lists |
| `local_repo_cache.py` | Reads/writes the per-project JSON cache file safely across threads |
| `config.py` | Parses `.env` into `ProjectConfig` objects, one per `PROJECT_X` |
| `project_tracker.py` | Builds PR stats/summaries for a single project, fetching repos in parallel |
| `multiple_project_tracker.py` | Builds aggregated stats across all projects, fetching projects in parallel |
| `threading_utils.py` | `run_parallel()` — shared helper wrapping `ThreadPoolExecutor` + `as_completed` |
| `cli.py` | Argument parsing, command dispatch, and Rich-formatted console output |

---

## 🛠 Dev Setup

**1. Create the virtual environment:**
```bash
python -m venv venv
```

**2. Activate it:**

| Platform | Shell | Command |
|---|---|---|
| Mac / Linux | Terminal / Zsh | `source venv/bin/activate` |
| Windows | Git Bash | `source venv/Scripts/activate` |
| Windows | PowerShell | `.\venv\Scripts\Activate.ps1` |
| Windows | Command Prompt | `venv\Scripts\activate.bat` |

**3. Install in editable mode:**
```bash
pip install -e .
```

**4. Run:**
```bash
python -m dev_tracker
```