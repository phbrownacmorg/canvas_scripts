#! /usr/bin/python3

# Functions for performing course backups

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast
import argparse
import json
import subprocess
import sys
import time
import urllib.parse
from read_courses import print_course, read_course_list
from upload_csv import constants, get_access_token, bytesOrStrPrintable

def start_course_backup(course_ID: int) -> dict[str, Any]:
    """Initiate a course backup for COURSE.  Return the result of the course backup, as a dictionary."""
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
            '--header', 'Authorization: Bearer ' + token,
            '--form', 'export_type=common_cartridge',
            '--form', 'skip_notifications=true',
            'https://{0}/api/v1/courses/{1}/content_exports'.format(constants()['host'],
                                                                    course_ID)]
    output:str = bytesOrStrPrintable(subprocess.check_output(cmd))
    #print(output)
    data: dict[str, Any] = json.loads(output)
    return data

def check_for_backup(course_id: int) -> dict[str, Any]:
    """Find out whether Canvas has a completed backup for the given COURSE_ID."""
    result: dict[str, Any] = {}
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
            '--header', 'Authorization: Bearer ' + token,
            'https://{0}/api/v1/courses/{1}/content_exports'.format(constants()['host'],
                                                                    course_id)]
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    data: list[dict[str, Any]] = json.loads(output)
    if len(data) > 0:
        result = data[0]
    return result

def recent(ISO_timestring: str) -> bool:
    """Takes a datetime string in ISO format, and returns True if it is sufficiently
    recent.  For this purpose "sufficiently recent" means less than a week old."""
    result = True
    if ISO_timestring.endswith('Z'):
        ISO_timestring = ISO_timestring[:-1] + '+00:00'
    then: datetime = datetime.fromisoformat(ISO_timestring)
    now: datetime = datetime.now(timezone.utc)

    if then > now:
        result = False
    else:
        age: timedelta = now - then
        max_age: timedelta = timedelta(7)
        result = (age < max_age)

    return result

def maybe_create_backup(course_id: int) -> dict[str, Any]:
    """Poll Canvas to see when the given BACKUP_ID for the given COURSE_ID is complete.
    Effectively busy-wait until it does complete, albeit with a maximum number of tries."""

    # Does the backup already exist?
    data: dict[str, Any] = check_for_backup(course_id)
    if 'export_type' not in data or 'created_at' not in data \
            or data['export_type'] != 'common_cartridge' \
            or not recent(data['created_at']):  # No usable backup exists for this course
        print('starting backup', end='', flush=True)
        data = start_course_backup(course_id)
    elif 'attachment' in data and data['workflow_state'] == 'exported':
        print('backed up', end=' ', flush=True)
    else:
        print('backing up', end='', flush=True)

    return data

def wait_for_completion(course_id: int) -> dict[str, Any]:
    completed = False
    max_tries = 90
    tries: int = 0
    delay = 12
    data = {}
    
    while not completed:
        data = check_for_backup(course_id)
        if 'attachment' in data and data['export_type'] == 'common_cartridge' and data['workflow_state'] == 'exported':
            completed = True
            break

        time.sleep(delay)
        tries += 1
        endstr = ''
        if tries % (60 // delay) == 0:
            endstr = ' '
        print('.', end=endstr, flush=True)

        if tries >= max_tries:
            raise Exception("Maximum tries exceeded")

    print(' ', end='', flush=True)
    # if not data['attachment']:
    #     print(data)    
    return cast(dict[str, Any], data['attachment'])

def maybe_download_backup(term: str, output_dir: Path, course: dict[str, Any]) -> None:
    """If the file doesn't already exist, download the backup file and store
       it in the proper directory with the right filename."""
    backup_data = wait_for_completion(course['canvas_course_id'])
    
    filename = term + '_' + course['course_id'].replace('/', '+') + '_' + backup_data['filename']
    filepath = output_dir.joinpath(filename)

    if filepath.exists() and filepath.stat().st_size == backup_data['size']:
        print('downloaded already')
    else:
        urlparts = urllib.parse.urlparse(backup_data['url'])
        queryparts = urllib.parse.parse_qs(urlparts.query)
        url = urllib.parse.urlunparse([urlparts.scheme, urlparts.netloc, urlparts.path, '',
                                       'verifier=' + queryparts['verifier'][0], ''])
        token = get_access_token()
        cmd = ['curl', '--no-progress-meter', '--show-error', '--location',
                '--header', 'Authorization: Bearer ' + token, 
                '--output-dir', str(output_dir), '--output', filename, url]
        # print(cmd)
        print('downloading', end=' ', flush=True)
        output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
        print(output)

# def get_course_backup(term: str, course: dict) -> None:
#     backup_data = create_or_find_backup(course['canvas_course_id'])
#     maybe_download_backup(term, course, backup_data)

def parse_args(argv: list[str]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(prog='course_backups.py')
    parser.add_argument('term', help='Term to back up')
    parser.add_argument('--start', default=0, type=int, 
                        help='Ordinal number (not ID) of course to start at')
    args = parser.parse_args(argv)
    return vars(args)

def main(argv: list[str]) -> int:
    args = parse_args(argv[1:])
    print(args, flush=True)
    term: str = cast(str, args['term'])

    backups_dir = Path.home().joinpath('Documents', 'DEd', 'course_backups')
    
    courselist: list[dict[str, Any]] = read_course_list(term, Path.joinpath(backups_dir, 'reports'))
    print(len(courselist), 'courses')
    # print_courses(courselist)

    print(time.asctime(), flush=True)
    #courselist = courselist[350:360]

    i: int = cast(int, args['start'])
    while i < len(courselist):
        print(i, end=' ')
        c = courselist[i]
        print_course(c, ': ')
        maybe_create_backup(c['canvas_course_id'])
        maybe_download_backup(term, backups_dir, c)
        i += 1
    # for c in courselist:
    #     print_course(c, ': ')

    print(time.asctime(), flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))