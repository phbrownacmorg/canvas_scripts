#! /usr/bin/python3

# Functions for performing course backups

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import subprocess
import sys
import time
import urllib.parse
from filter_csv import read_from_csv
from upload_csv import constants, get_access_token, bytesOrStrPrintable

def print_course(course: dict, endstr: str = '\n') -> None:
    print(course['canvas_course_id'], course['short_name'], course['status'], end=endstr, flush=True)

def print_courses(courses: list[dict]) -> None:
    for course in courses:
        print_course(course)

def read_course_list(term: str) -> list[dict]:
    reportsdir = Path.home().joinpath('Documents', 'DEd', 'Canvas', 'course_backups', 'reports')
    # print(reportsdir)
    courses: list[dict] = read_from_csv(reportsdir.joinpath(term + '-courses.csv'))
    courses = [c for c in courses if c['status'] == 'active'] # Filter out any courses that were not published

    # Filter out courses that were cross-listed, even if they were published
    xlist: list[dict] = read_from_csv(reportsdir.joinpath(term + '-xlist.csv'))
    xlist_nums = [item['canvas_nonxlist_course_id'] for item in xlist]
    #print(xlist_nums)
    courses = [c for c in courses if c['canvas_course_id'] not in xlist_nums]
    courses.sort(key=lambda c : c['short_name'])
    #result = [c['canvas_course_id'] for c in courses]

    return courses

def start_course_backup(course_ID: int) -> dict:
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
    data = json.loads(output)
    return data

def check_for_backup(course_id: int) -> dict:
    """Find out whether Canvas has a completed backup for the given COURSE_ID."""
    result: dict = {}
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
            '--header', 'Authorization: Bearer ' + token,
            'https://{0}/api/v1/courses/{1}/content_exports'.format(constants()['host'],
                                                                    course_id)]
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    data: list[dict] = json.loads(output)
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

def maybe_create_backup(course_id: int) -> dict:
    """Poll Canvas to see when the given BACKUP_ID for the given COURSE_ID is complete.
    Effectively busy-wait until it does complete, albeit with a maximum number of tries."""

    # Does the backup already exist?
    data: dict = check_for_backup(course_id)
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

def wait_for_completion(course_id: int) -> dict:
    completed = False
    max_tries = 90
    tries: int = 0
    delay = 10
    
    while not completed:
        data = check_for_backup(course_id)
        if 'attachment' in data and data['export_type'] == 'common_cartridge' and data['workflow_state'] == 'exported':
            completed = True
            break

        time.sleep(delay)
        tries += 1
        endstr = ''
        if tries % 10 == 0:
            endstr = ' '
        print('.', end=endstr, flush=True)

        if tries >= max_tries:
            raise Exception("Maximum tries exceeded")

    print(' ', end='', flush=True)
    # if not data['attachment']:
    #     print(data)    
    return data['attachment']

def maybe_download_backup(term: str, course: dict) -> None:
    """If the file doesn't already exist, download the backup file and store
       it in the proper directory with the right filename."""
    backup_data = wait_for_completion(course['canvas_course_id'])
    output_dir = Path.home().joinpath('Documents', 'DEd', 'Canvas', 'course_backups')
    filename = term + '_' + course['short_name'].replace('/', '+') + '_' + backup_data['filename']

    if output_dir.joinpath(filename).exists():
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

def main(argv: list[str]) -> int:
    term: str = '2223-SP'
    courselist: list[dict] = read_course_list(term)
    print(len(courselist), 'courses')
    #print_courses(courselist)
    print(time.asctime(), flush=True)
    # courselist = courselist[:10]
    for c in courselist:
        print_course(c, ': ')
        maybe_create_backup(c['canvas_course_id'])
        maybe_download_backup(term, c)
    # for c in courselist:
    #     print_course(c, ': ')

    print(time.asctime(), flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))