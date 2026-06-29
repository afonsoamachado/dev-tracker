# Repo Tracker

A cross-platform CLI tool built in Python to monitor your Azure DevOps Pull Requests across multiple projects.

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

Repository lists are cached locally in `azure_devops/.cache/repositories.json` to avoid redundant API calls on every run.

The cache is **automatically invalidated** when you change `PROJECT_*_REPOS` in your `.env`. Use `--refresh` to force a fresh fetch if you've added new repos directly in Azure DevOps:

```bash
dev-tracker active --refresh
dev-tracker active PROJECT_1 --refresh
```

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