#! /usr/bin/python3.7

# Filter to correct the puncutation of users' fullnames for import to Canvas.
# Input comes from one CSV file, and output is written to another.
# Peter Brown <peter.brown@converse.edu>, 2020-07-27

import csv
from pathlib import Path
import re
from typing import Dict, List

from fix_course_fullnames import get_data_dirs, read_from_csv, write_outfile

# Fix initials in the long name.  I am brazenly assuming that we have no
# Harry S Trumans, and that every initial actually stands for something.
def fix_initials(fullname:str) -> str:
    fixed:str = re.sub(r' ([A-Z]) ', r' \1. ', fullname)
    # I know, I *could* combine the regexes
    fixed = re.sub(r'\b([A-Z]) ', r'\1. ', fixed)
    return fixed

# Filter the record for one user, removing empty and NULL fields and
# correcting the case of the course long_name.
def filter_one_course(inrec:Dict[str, str]) -> Dict[str, str]:
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

def filter_records(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    outrecords:List[Dict[str, str]] = []
    for record in inrecords:
        outrecords.append(filter_one_course(record))
    return outrecords


def main(argv:List[str]) -> int:
    infile:Path = get_data_dirs()['inputdir'].joinpath('users.csv')
    if len(argv) > 1:
        infile = Path(argv[1])
    inrecords:List[Dict[str, str]] = read_from_csv(infile)
    outrecords:List[Dict[str, str]] = filter_records(inrecords)
    print(outrecords)
    outfile:Path = get_data_dirs()['outputdir'].joinpath(infile.stem + '-fixed.csv')
    write_outfile(outrecords, outfile)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

