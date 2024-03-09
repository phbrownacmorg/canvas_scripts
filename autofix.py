#! /usr/bin/python3

# File to automatically fix when an upload fails to clear
# Peter Brown <peter.brown@converse.edu>, 2022-03-10

import subprocess
import sys
from pathlib import Path
from typing import cast
from csv_update import get_data_dirs
from upload_csv import last_upload_file, working_prefix

def fix_file(dir: Path) -> bool:
    """Fix the lock file, if it needs it and can be fixed.
    Return True if the lockfile was fixed, or False if it wasn't."""
    fixed: bool = False
    fname: Path = last_upload_file(dir)
    if fname.exists():
        contents: str = fname.read_text()
        # print('"' + contents + '"')
        if contents.startswith(working_prefix()):
            numstr: str = contents.replace(working_prefix(), '')
            # print('"' + numstr + '"')
            if numstr.strip().isdigit():
                fname.write_text(numstr)
                fixed = True
    # print('fix_file returning', fixed)
    return fixed

# Note that the Nagios check runs every 3 minutes
def rerun_job(dir: Path) -> int:
    cmd: list[str] = cast(list[str], [dir.joinpath('csv_update.py')])
    proc = subprocess.run(cmd, capture_output=True, timeout=150)
    return proc.returncode

def main(args: list[str]) -> int:
    # print('autofixing...')
    code: int = 0
    outputdir: Path = get_data_dirs()['outputdir']
    if fix_file(outputdir):
        # print('Fixed')
        code = rerun_job(outputdir)
    return code


if __name__ == '__main__':
    main(sys.argv)
            
    
