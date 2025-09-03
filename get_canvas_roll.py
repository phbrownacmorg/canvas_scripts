#! /usr/bin/python3

# FFunctions for extracting a Canvas class roll using the Canvas API.  Stores results in a Dropbox directory.

from pathlib import Path
from typing import Any
import json
import subprocess
import sys
from filter_csv import write_outfile
from upload_csv import constants, get_access_token, bytesOrStrPrintable

def course_id_from_code(course_code: str) -> str:
    """Given a course code, find the corresponding course ID."""
    id: str = ''
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
            '--header', 'Authorization: Bearer ' + token,
            'https://{0}/api/v1/accounts/1/courses?enrollment_type[]=student&published=true&search_by=course&search_term={1}'.format(
                constants()['host'], course_code)]
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    #print(output)
    data: list[dict[str, Any]] = json.loads(output)
    #print(data)
    assert(len(data) == 1)
    id = str(data[0]['id'])
    return id

def get_course_roll(course_id: str) -> list[dict[str, Any]]:
    """Given a course ID, get the student roll."""
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
            '--header', 'Authorization: Bearer ' + token,
            'https://{0}/api/v1/courses/{1}/users?enrollment_type[]=student&sort=sortable_name&per_page=100'.format(
                constants()['host'], course_id)]
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    # print(output)
    # find the JSON in the output

    data: list[dict[str, Any]] = json.loads(output)
    return data

def normalize_fields(inrecords: list[dict[str, Any]], include_all_fields: bool = False) -> list[dict[str, str]]:
    """Takes a set of input records INRECORDS, and returns a normalized version.
        In the normalized version, all the dictionaries in the list have the
        same set of headers, and the values for all the keys are strings."""
    # Find all the fields present in any of the records
    fields = ['id', 'sis_user_id', 'name', 'sortable_name', 'short_name', 'pronouns', 'login_id', 'email', 'created_at']
    # Include all the fields if desired, but usually don't bother.
    if include_all_fields:
        for rec in inrecords:  # The looping approach preserves the order of fields
            for key in rec.keys():
                if key not in fields:
                    fields.append(key)

    # Normalize the values
    outrecords: list[dict[str, str]] = []
    for inrec in inrecords:
        outrec: dict[str, str] = {}
        for field in fields:
            outrec[field] = str(inrec.get(field, ''))
        outrecords.append(outrec)        

    return outrecords


def main(args: list[str]) -> int:
    course_code: str = 'HPE125.01-2526-FA'
    if (len(args) > 1):
        course_code = args[1]
    print('Course code:', course_code)
    course_id: str = course_id_from_code(course_code)
    print('Course ID:', course_id)
    roll: list[dict[str, Any]] = get_course_roll(course_id)
    print('Got', len(roll), 'users')
    roll = normalize_fields(roll)
    #print(roll)
    roll_file_dir = Path.home().joinpath('Dropbox', 'DEd', 'Canvas', 'rolls')
    write_outfile(roll, roll_file_dir.joinpath(course_code + "_roll.csv"))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))