from pathlib import Path
import script_helpers as scripts

# Create virtual environment if not present
def ensure_virtual_environment():
    project_root_path = scripts.get_project_root_path()
    if (not((project_root_path / '.venv').exists())):
        print("Virtual environment not found. Creating one now.")
        scripts.run_command(['venv', '.venv'], use_venv=False)

if __name__ == "__main__":
    ensure_virtual_environment()

    # Update pip
    scripts.run_command(['pip', 'install', '--upgrade', 'pip'])

    # Install project reqirements
    scripts.run_command(['pip', 'install', '-r', scripts.REQUIREMENTS_FILENAME])
