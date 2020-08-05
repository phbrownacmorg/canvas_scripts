#! /usr/bin/python3.8

# Filter to add training-course enrollments to enrollments.csv
# Input comes from one CSV file, and output is written to another.
# Peter Brown <peter.brown@converse.edu>, 2020-07-31

import csv
from pathlib import Path
import re
from typing import Dict, List

from fix_course_fullnames import get_data_dirs, read_from_csv, write_outfile

def filter_records(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    outrecords:List[Dict[str, str]] = []
    students = set()
    teachers = set()
    for record in inrecords:
        outrecords.append(record)
        if record['role'] == 'student':
            students.add(record['user_id'])
        elif record['role'] == 'teacher':
            teachers.add(record['user_id'])

    for s in students:
        record:Dict[str, str] = {'course_id': 'passport_to_canvas',
                                 'root_account': '', 'user_id': s, 'user_integration_id': '',
                                 'role': 'student', 'section_id': '','status': 'active',
                                 'associated_user_id': '', 'limit_section_priveleges': '' }
        outrecords.append(record)

    for t in teachers:
        record:Dict[str, str] = {'course_id': 'growing_with_canvas',
                                 'root_account': '', 'user_id': s, 'user_integration_id': '',
                                 'role': 'student', 'section_id': '','status': 'active',
                                 'associated_user_id': '', 'limit_section_priveleges': '' }
        outrecords.append(record)
                                 
    return outrecords
# Next: try to run, see what happens.

def main(argv:List[str]) -> int:
    infile:Path = get_data_dirs()['inputdir'].joinpath('Enrollments.csv')
    if len(argv) > 1:
        infile = Path(argv[1])
    inrecords:List[Dict[str, str]] = read_from_csv(infile)
    outrecords:List[Dict[str, str]] = filter_records(inrecords)
    print(outrecords[:10])
    outfile:Path = get_data_dirs()['outputdir'].joinpath(infile.stem + '-fixed.csv')
    write_outfile(outrecords, outfile)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

