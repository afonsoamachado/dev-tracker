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

4. Run:
```bash
dev-tracker <command>
```

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
pip install -r requirements-lock.txt
```

**4. Run the Application**

```bash
python -m dev_tracker
```

**5. Install**
```bash
pip install -e .
```