#! /usr/bin/python3

# Functions for attempting to get attendance reports from Canvas
# Peter Brown <peter.brown@converse.edu>, 2021-02-19

import subprocess
import sys
from typing import List
from upload_csv import constants, get_access_token, bytesOrStrPrintable

def main(argv:List[str]) -> int:

    # get sessionless URL
    token:str = get_access_token()
    cmd = ['curl',
           '-H', "Authorization: Bearer " + token,
           '-F', 'id=4',
           '-o', 'attendance-out.html',
           'https://' + constants()['host'] + '/api/v1/accounts/1/external_tools/sessionless_launch']

    # Lots of ways for things to go wrong in here, none of which can
    # reasonably be caught.  Therefore, don't bother with try-except.
    output = bytesOrStrPrintable(subprocess.check_output(cmd))
    # resultval = json.loads(output)
    print(output)
    
    return 0
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))

