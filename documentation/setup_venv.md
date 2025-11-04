# Setting Up Virtual Environment for Analysis Model

## Creating and Using a Virtual Environment

### Step 1: Create Virtual Environment

```powershell
# Navigate to the analysis-model directory
cd "d:\Study Folder\Coding Folders (VsCode)\Web programming\PJT-1\Geo-Temporal-Trend-Detection-on-Reddit\analysis-model"

# Create a virtual environment named 'venv'
python -m venv venv
```

### Step 2: Activate Virtual Environment

```powershell
# Activate the virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` appear at the beginning of your command prompt.

### Step 3: Install Dependencies

```powershell
# With venv activated, install all requirements
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### Step 4: Run Your Code

```powershell
# Run the model (venv must be activated)
python model.py

# Run the API server (venv must be activated)
python api.py
```

### Step 5: Deactivate When Done

```powershell
# Deactivate the virtual environment
deactivate
```

## Deleting the Virtual Environment

To completely remove all installed packages:

```powershell
# Make sure venv is deactivated first
deactivate

# Delete the venv folder
Remove-Item -Recurse -Force venv
```

## Using VS Code with Virtual Environment

1. Open Command Palette: `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. Choose the interpreter from `.\venv\Scripts\python.exe`

VS Code will automatically activate the venv when you open a terminal.

## Checking What's Installed

```powershell
# With venv activated, list all installed packages
pip list

# See only the packages from requirements.txt
pip freeze
```

## Benefits of Using venv

- ✅ Isolated environment - doesn't affect system Python
- ✅ Easy to delete - just remove the `venv` folder
- ✅ Reproducible - same dependencies across machines
- ✅ No conflicts with other Python projects
- ✅ Easy to recreate - just run `pip install -r requirements.txt` again

## Quick Reference

```powershell
# Create venv
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (CMD)
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate

# Delete venv
Remove-Item -Recurse -Force venv
```
