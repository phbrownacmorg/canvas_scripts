#! /usr/bin/python3

# Filter to correct the punctuation of users' fullnames for import to Canvas.
# Peter Brown <peter.brown@converse.edu>, 2020-07-27
# Changed from a standalone program to a library, 2020-08-04

import re
from typing import Dict, List

# Fix initials in the long name.  I am brazenly assuming that we have no
# Harry S Trumans, and that every initial actually stands for something.
def fix_initials(fullname:str) -> str:
    fixed:str = re.sub(r' ([A-Z]) ', r' \1. ', fullname)
    # I know, I *could* combine the regexes
    fixed = re.sub(r'\b([A-Z]) ', r'\1. ', fixed)
    return fixed

# Filter the record for one user, removing empty and NULL fields and
# correcting the case of the course long_name.
def filter_one_user(inrec:Dict[str, str]) -> Dict[str, str]:
    values_to_ignore = ['', 'NULL', '00:00.0']
    keys_to_ignore = ['integration_id', 'password']
    outrec:Dict[str, str] = {}
    for key in inrec.keys():
        if key not in keys_to_ignore:
            value = inrec[key]
            if key == 'full_name':
                outrec['full_name'] = fix_initials(value)
            elif value not in values_to_ignore:
                outrec[key] = value
            else:
                outrec[key] = ''
    return outrec

# Determine if a record is valid for input to Canvas.  Currently, this
# filters out folks who have a login_id that isn't a Converse email
# address.
def valid_for_input(record:Dict[str, str]) -> bool:
    result:bool = True
    if not record['login_id'].endswith('@converse.edu'):
        result = False
    return result

# Takes a list of user records, each one a dictionary, filters them,
# and returns the result of that filtering.
def filter_users(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    outrecords:List[Dict[str, str]] = []
    for record in inrecords:
        if valid_for_input(record):
            outrecords.append(filter_one_user(record))
    return outrecords
