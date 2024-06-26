
# Functions for uploading CSV files to Canvas.
# Peter Brown <peter.brown@converse.edu>, 2020-08-04

from datetime import datetime
from pathlib import Path
from typing import Any, cast, Union
import json
import os
import subprocess
import time

# Set constants, using a dict instead of global variables
def constants() -> dict[str, str]:
    return { #'host': 'converse.beta.instructure.com',
             'host': 'converse.instructure.com',
             'tokenfile': 'tokens.json' }

# Get the access token for the host we're using
def get_access_token(suffix:str = '') -> str:
    tokfile = Path.home().joinpath('.ssh', (constants()['tokenfile']))
    data: dict[str, Any] = json.loads(tokfile.read_text())
    key: str = constants()['host'] + suffix
    #print(key)
    return cast(str, data[key])

def last_upload_file(dir:Path) -> Path:
    return dir.joinpath(constants()['host'] + '-upload.txt')

# Out here so it can be imported elsewhere
def working_prefix() -> str:
    return 'Working:'

def working_msg(pid: int, last_upload: int) -> str:
    return working_prefix() + ' pid {0} last was {1}'.format(pid, last_upload)

def timeout_prefix() -> str:
    return 'Timed out:'

def illegal_state_prefix() -> str:
    return 'Illegal state:'

# Record a case where the previous upload failed, but the recovery procedure
# was automated.
def record_saving_throw(dir: Path, contents: str) -> None:
    record_fname: Path = dir.joinpath('saving_throws.txt')
    msg: str = str(datetime.now()) + ': ' + contents + '\n'
    with open(record_fname, 'a') as f:
        f.write(msg)

# Get the ID number of the last upload from the file where it's stored.
# If there is no such file, just return -1 (no job).
def get_last_upload(dir: Path) -> int:
    last_upload: int = -1
    prefix: str = ''
    fname: Path = last_upload_file(dir)
    if fname.exists():
        contents: str = fname.read_text()
        tokens: list[str] = contents.split()
        last_upload = int(tokens[-1]) # If the last token isn't a number, we're done.
        prefix = ' '.join(tokens[:-1]) # Returns '' if the number is the only thing

        if prefix == illegal_state_prefix():
            raise RuntimeError(contents)
        elif prefix.startswith(timeout_prefix()):
            record_saving_throw(dir, contents)
        elif prefix.startswith(working_prefix()):
            # Check whether the PID is still running
            pid: int = int(tokens[2])
            cmd = ['ps', '--no-headers', '--format', 
                   'pid,stat,time,cmd', '--pid',
                   str(pid)]
            try:
                output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
            except subprocess.CalledProcessError as e:
                record_saving_throw(dir, contents)
                output = e.output
            else:
                # Still running, raise RuntimeError
                raise RuntimeError(contents)

	# os.pid() to get current PID
        # os.kill(pid, signal); signal is signal.SIGKILL on Unix
        # I see nothing to query the status of another process; use 'ps" instead
        # ps --format pid,stat,time,cmd --no-headers --pid pid
        # output iff the proc exists

    # If a task starts before this one ends, make the other one fail fast.
    # The other one will try to read a number from the file and crash.
    # Effectively, this provides a file lock for the process.
    fname.write_text(working_msg(os.getpid(), last_upload))

    return last_upload

# Write the ID number of the last upload to the file.
# Alternatively, a preformatted message can be written.
def write_last_upload(idnum: Union[int, str], dir: Path) -> None:
    fname:Path = last_upload_file(dir)
    fname.write_text(str(idnum))

# Take a byte sequence or a string and return a string, so it's known
# to be printable.
def bytesOrStrPrintable(instring: Union[str, bytes]) -> str:
    """Take a bytestring or string INSTRING and convert it to a string."""
    outstring = instring
    try:
        outstring = instring.decode('utf-8') # type: ignore
    except AttributeError: # It's already a string, leave it alone
        pass
    return cast(str, outstring)

# Check whether the upload with id IDNUM has finished yet.
def upload_complete(idnum: int) -> bool:
    complete = (idnum == -1)
    if not complete:
        token = get_access_token()
        cmd = ['curl', '--silent', '--show-error', 
               '-H', "Authorization: Bearer " + token,
               ('https://{0}/api/v1/accounts/self/sis_imports/' +
                '{1}').format(constants()['host'], idnum)]
        output:str = bytesOrStrPrintable(subprocess.check_output(cmd))
        #print(output)
        data = json.loads(output)
        if data['progress'] == 100 \
           and data['workflow_state'].startswith('imported'):
            complete = True
        elif data['workflow_state'] not in ('created', 'importing'):
            print(output)
            raise RuntimeError(illegal_state_prefix() + ' ' + str(idnum))
        else:
            # Gives some visual feedback if we have to wait for completion
            print(data['progress'], data['workflow_state'])
    return complete

# Wait for the upload with id LAST_UPLOAD to complete, using a loop.
# If the upload takes *too* long, raise an exception.
def wait_for_upload_complete(last_upload: int) -> bool:
    max_wait = 1000 # Max time to wait (seconds)
    wait_step = 5  # Wait time each time around the loop (seconds)
    waited = 0     # Time waited so far (seconds)
    while waited < max_wait and not upload_complete(last_upload):
        waited = waited + wait_step
        time.sleep(wait_step)
    if waited >= max_wait:
        raise RuntimeError(timeout_prefix() + ' ' + str(last_upload))
    return True # If we get here, the upload completed successfully

# Upload a CSV file to Canvas.  Return the ID of the upload job, so it
# can be checked whether the job is done before starting another.
def upload(stem: str, dir: Path, last_upload: int) -> int:
    # First, figure out if the previous upload succeeded.
    wait_for_upload_complete(last_upload)

    # Next, do this upload
    token = get_access_token()
    cmd = ['curl', '--silent', '--show-error',
           '-F', 'attachment=@' + str(dir.joinpath(stem + '.csv')),
           '-H', "Authorization: Bearer " + token,
           'https://' + constants()['host'] + '/api/v1/accounts/self/sis_imports.json?import_type=instructure_csv']
    # Lots of ways for things to go wrong in here, none of which can
    # reasonably be caught.  Therefore, don't bother with try-except.
    output = bytesOrStrPrintable(subprocess.check_output(cmd))
    resultval = json.loads(output)
    uploadID: int = cast(int, resultval['id'])
    print('Upload ID:', uploadID)
    print()
    return uploadID
