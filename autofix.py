#! /usr/bin/python3

# File to automatically fix when an upload fails to clear
# Peter Brown <peter.brown@converse.edu>, 2022-03-10

from pathlib import Path
from csv_update import get_data_dirs
from upload_csv import last_upload_file, working_prefix
import subprocess

def fix_file(dir: Path) -> bool:
    """Fix the lock file, if it needs it and can be fixed.
    Return True if the lockfile was fixed, or False if it wasn't."""
    fixed: bool = False
    fname: Path = last_upload_file(dir)
    if fname.exists():
        contents: str = fname.read_text()
        if contents.startswith(working_prefix()):
            numstr: str = contents.substitute(working_prefix(), '')
            if numstr.isdigit():
                fname.write_text(numstr)
                fixed = True
    return fixed

# Note that the Nagios check runs every 3 minutes
def rerun_job(dir: Path) -> int:
    cmd: list[str] = [dir.joinpath('csv_update.py')]
    proc: subprocess.CompletedProcess = \
            subprocess.run(cmd, capture_output=True, timeout=150)
    return proc.returncode

def main(argv: list[str]) -> int:
    code: int = 0
    outputdir: Path = get_data_dirs()['outputdir']
    if fix_file(outputdir):
        code = rerun_job(outputdir)
    return code
            

            
            
    
