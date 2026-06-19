# Repo Tracker

A cross-platform CLI tool built in Python to monitor your Azure DevOps Pull Requests.

## 🚀 Quick Start
1. Create your .env file:
```bash
cp .env.example .env
```

2. Fill in your Azure DevOps details in .env:
   - `AZURE_DEVOPS_ORG` - Your organization name
   - `AZURE_DEVOPS_PAT` - Your personal access token
   - `PROJECT_X_NAME` - Project names
   - `PROJECT_X_REPOS` - Repos to track per project

3. Run the tracker:

**With venv activated (recommended):**
```bash
source venv/bin/activate
python main.py menu       # Interactive menu - choose summary or active PRs
python main.py summary    # Show PR statistics for ALL projects
python main.py active     # List all open PRs across ALL projects
python main.py help       # Show all commands
```

**Interactive Mode (Live Auto-Refresh):**
```bash
python main.py interactive              # All projects, 60s refresh (default)
python main.py interactive PROJECT_1    # Single project, 60s refresh
python main.py interactive all 30       # All projects, 30s refresh
python main.py interactive PROJECT_2 45 # Single project, 45s refresh
```
Press `Ctrl+C` to exit interactive mode.

## 📋 Menu Mode (Navigate Summary & Active PRs)

For an easy interactive experience, use the menu mode:

```bash
python main.py menu
```

**Features:**
- Choose between Summary and Active PRs views
- Select specific projects or view all
- Easy navigation back to menu
- Type `q` to quit at any time

**Or run directly without activation:**
```bash
./venv/bin/python main.py summary
```

**Or specify a single project:**
```bash
python main.py summary PROJECT_1
python main.py active PROJECT_2
```

## 🔄 Interactive Mode (Auto-Refresh)

For live monitoring, use interactive mode to get automatic updates without manual reruns:

```bash
python main.py interactive              # Default: all projects, 60s refresh
python main.py interactive PROJECT_1 30 # Single project, 30s refresh
```

**Features:**
- Auto-refreshes at configurable interval
- Shows last update timestamp
- Press `Ctrl+C` to exit
- Great for dashboards and monitoring

🔑 Where to Get Your Personal Access Token
Go to: https://dev.azure.com/{your-organization}
Click your profile picture → Personal access tokens
Click New Token
Set these options:
Name: repo-tracker
Scopes: Code (Read) ✓
Expiration: Set as needed
Click Create and copy the token


## DEV Setup

**1. Create the Virtual Environment**
```bash
python -m venv venv
```

**2. Activate the Environment (Recommended)**

Activation isolates your dependencies and is recommended for development. Choose your OS:

* **Mac / Linux (Terminal/Zsh):**
```bash
source venv/bin/activate
```

* **Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

* **Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

* **Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

*Note: After activation, your terminal will show `(venv)` prefix. To deactivate later: `deactivate`*

**Alternative: Run without activation**
```bash
./venv/bin/python main.py summary
```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the Application**

```bash
python main.py
```