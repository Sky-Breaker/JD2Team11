import os
import subprocess
from pathlib import Path

REQUIREMENTS_FILENAME = 'requirements.txt'

def is_dir_in_project_root(directory: str):
    scripts_path = Path(__file__) # __file__ is an attribute that gives the absolute path of this script file

    # Tell os library to go to this file ^ scripts ^ project root
    project_root_path = scripts_path.parent.parent
    os.chdir(project_root_path)

    return (project_root_path / directory).exists() # Check for given directory in root

if __name__ == "__main__":
    # Create virtual environment if not present
    if (not(is_dir_in_project_root('.venv'))):
        print("Virtual environment not found. Creating one now.")
        subprocess.run(
            ['python', '-m', 'venv', '.venv'],
            text=True,
            check=True
        )

    # Does not work without using .venv
    # # Update pip
    # subprocess.run(
    #     ['python', '-m', 'pip', 'install', '--upgrade', 'pip'],
    #     text=True,
    #     check=True 
    # )

    # # Install project reqirements
    # subprocess.run(
    #     ['python', '-m', 'pip', 'install', '-r', REQUIREMENTS_FILENAME],
    #     text=True,
    #     check=True
    # )

