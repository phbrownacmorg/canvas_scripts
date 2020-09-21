#! /usr/bin/python3.8

# Functions for uploading CSV files to Canvas.
# Peter Brown <peter.brown@converse.edu>, 2020-08-04

import json
from pathlib import Path
import subprocess
import time
from typing import cast, Dict, List, Union

# Set constants, using a dict instead of global variables
def constants() -> Dict[str, str]:
    return { #'host': 'converse.beta.instructure.com',
             'host': 'converse.instructure.com',
             'tokenfile': 'tokens.json' }

# Get the access token for the host we're using
def get_access_token() -> str:
    tokfile = Path.home().joinpath('.ssh', (constants()['tokenfile']))
    data = json.loads(tokfile.read_text())
    return data[constants()['host']]

def last_upload_file(dir:Path) -> Path:
    return dir.joinpath(constants()['host'] + '-upload.txt')

# Get the ID number of the last upload from the file where it's stored.
# If there is no such file, just return -1 (no job).
def get_last_upload(dir:Path) -> int:
    last_upload:int = -1
    fname:Path = last_upload_file(dir)
    if fname.exists():
        # The number should be the only thing in the file.
        last_upload = int(fname.read_text()) 
        
    # If a task starts before this one ends, make the other one fail fast.
    # The other one will try to read a number from the file and crash.
    # Effectively, this provides a file lock for the process.
    fname.write_text('Working: last was ' + str(last_upload))

    return last_upload

# Write the ID number of the last upload to the file
def write_last_upload(idnum:int, dir:Path) -> None:
    fname:Path = last_upload_file(dir)
    fname.write_text(str(idnum))

# Take a byte sequence or a string and return a string, so it's known
# to be printable.
def bytesOrStrPrintable(instring:Union[str,bytes]) -> str:
    """Take a bytestring or string INSTRING and convert it to a string."""
    outstring = instring
    try:
        outstring = instring.decode('utf-8') # type: ignore
    except AttributeError: # It's already a string, leave it alone
        pass
    return cast(str, outstring)

# Check whether the upload with id IDNUM has finished yet.
def upload_complete(idnum:int) -> bool:
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
            raise RuntimeError(('Import {0} is neither done nor'
                                + ' importing').format(idnum))
        else:
            # Gives some visual feedback if we have to wait for completion
            print(data['progress'], data['workflow_state'])
    return complete

# Wait for the upload with id LAST_UPLOAD to complete, using a loop.
# If the upload takes *too* long, raise an exception.
def wait_for_upload_complete(last_upload:int) -> bool:
    max_wait = 1000 # Max time to wait (seconds)
    wait_step = 5  # Wait time each time around the loop (seconds)
    waited = 0     # Time waited so far (seconds)
    while waited < max_wait and not upload_complete(last_upload):
        waited = waited + wait_step
        time.sleep(wait_step)    
    if waited >= max_wait:
        raise RuntimeError('Import {0} took too long'.format(last_upload))
    return True # If we get here, the upload completed successfully

# Upload a CSV file to Canvas.  Return the ID of the upload job, so it
# can be checked whether the job is done before starting another.
def upload(stem:str, dir:Path, last_upload:int) -> int:
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
    uploadID = resultval['id']
    print(uploadID)
    print()
    return uploadID
