# Repo Tracker

A cross-platform CLI tool built in Python to monitor your Azure DevOps Pull Requests.

## 🚀 Quick Start Setup

**1. Create the Virtual Environment**
```bash
python -m venv venv

```

**2. Activate the Environment**

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



**3. Package Management (pip)**

* **Install new packages:**
```bash
pip install requests python-dotenv rich

```


* **Save installed packages to a file:**
```bash
pip freeze > requirements.txt

```


* **Install all packages from a file (after cloning):**
```bash
pip install -r requirements.txt

```



**4. Run the Application**

```bash
python main.py

```