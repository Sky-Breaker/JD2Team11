from pathlib import Path
import script_helpers as scripts

if __name__ == "__main__":
    # Run pip freeze command to generate requirements file
    result = scripts.run_command(['pip', 'freeze'], capture_output=True)
    
    project_root_path = scripts.get_project_root_path()
    (project_root_path / scripts.REQUIREMENTS_FILENAME).write_text(result.stdout)
    print(f"Created {scripts.REQUIREMENTS_FILENAME}")