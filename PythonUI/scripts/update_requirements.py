import os
import subprocess
from pathlib import Path

REQUIREMENTS_FILENAME = 'requirements.txt'

if __name__ == "__main__":
    result = subprocess.run(
        ['python', '-m', 'pip', 'freeze'],
        capture_output=True,
        text=True,
        check=True
    )

    Path(REQUIREMENTS_FILENAME).write_text(result.stdout)
    print(f"Created {REQUIREMENTS_FILENAME}")