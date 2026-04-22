import os
import subprocess
from pathlib import Path

REQUIREMENTS_FILENAME = 'requirements.txt'

def get_project_root_path():
    # __file__ is an attribute that gives the absolute path to this script file
    scripts_path = Path(__file__)

    # Tell os library to look at this file ^ scripts ^ project root
    project_root_path = scripts_path.parent.parent
    os.chdir(project_root_path)

    return project_root_path

def _get_python_path(use_venv: bool):
    project_root_path = get_project_root_path()
    venv_exists = (project_root_path / '.venv').exists()
    if (use_venv and venv_exists):
        # Find correct venv python path for OS
        if (os.name == "nt"):
            # Windows venv python path
            return project_root_path / '.venv' / 'Scripts' / 'python.exe'
        else:
            # Other system venv python path
            return project_root_path / '.venv' / 'bin'/ 'python'
    else:
        return 'python'

def run_command(args: list[str], capture_output=False, use_venv: bool=True):
    python = str(_get_python_path(use_venv))
    print('Running:', python + ' -m ' + " ".join(args))
    # Run a terminal command using subprocess library
    result = subprocess.run(
        [python, '-m'] + args, # Add {Python executable} -m in front of args so the command is run in the correct environment
        capture_output=capture_output,
        text=True,
        check=True
    )
    return result
