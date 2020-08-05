#! /usr/bin/python3.8

# Filter to correct the case of course fullnames for import to Canvas.
# Input comes from one CSV file, and output is written to another.
# Peter Brown <peter.brown@converse.edu>, 2020-08-04

import json
from pathlib import Path
import subprocess
from typing import cast, Dict, List, Union

def bytesOrStrPrintable(instring:Union[str,bytes]) -> str:
    """Take a bytestring or string INSTRING and convert it to a string."""
    outstring = instring
    try:
        outstring = instring.decode('utf-8') # type: ignore
    except AttributeError: # It's already a string, leave it alone
        pass
    return cast(str, outstring)

def upload(stem:str, dir:Path, last_upload:int) -> int:
    # First, figure out if the last upload succeeded.
    

    # Next, do this upload
    cmd = ['curl', '-F', 'attachment=@' + str(dir.joinpath(stem + '.csv')),
           '-H', "Authorization: Bearer 16425~OKYWUQchnjal3ISR54KzqhYzByMhMLOk3z1aqbMtlLEg8qgDzipyOL6NtFF1eE9k", 'https://converse.beta.instructure.com/api/v1/accounts/self/sis_imports.json?import_type=instructure_csv']

    returncode = 0
    output:str = '(none)'
    uploadID = 0
    
    try:
        output = bytesOrStrPrintable(subprocess.check_output(cmd))
    except subprocess.CalledProcessError as e:
        print('\n----------------ERRORS-----------------\n')
        print(bytesOrStrPrintable(e.output))
        returncode = e.returncode
    else:
        print('\n----------------OUTPUT-----------------\n')
        print(output)

        # Extract the ID
        
        try:
            resultval = json.loads(output)
            uploadID = resultval['id']
        except json.JSONDecodeError as err:
            print('\n----------------JSON ERRORS-----------------\n')
            print(bytesOrStrPrintable(e.output))
        else:
            print(resultval)
            print(uploadID)
    print()
    return uploadID
