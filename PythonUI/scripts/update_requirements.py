import subprocess
from pathlib import Path

FILENAME = 'requirements.txt'

if __name__ == "__main__":
    result = subprocess.run(
        ['pip', 'freeze'],
        capture_output=True,
        text=True,
        check=True
    )

    path = Path(FILENAME).write_text(result.stdout)
    print(f"Created {FILENAME}")