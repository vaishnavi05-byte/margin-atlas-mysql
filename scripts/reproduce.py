"""One command: validate data, rebuild decision exports, prepare SQL and run tests."""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for command in [['src/build_decisions.py'],['scripts/prepare_mysql.py'],['-m','unittest','discover','-s','tests','-v']]:
    subprocess.run([sys.executable,*command],cwd=ROOT,check=True)
print('Reproduction succeeded. Native report definitions are preserved.')
