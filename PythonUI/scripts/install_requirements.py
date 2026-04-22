import subprocess
from pathlib import Path

FILENAME = 'requirements.txt'

if __name__ == "__main__":
    install_result = subprocess.run(
        ['pip', 'install', '-r', FILENAME],
        text=True,
        check=True
    )
