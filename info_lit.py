#! /usr/bin/python3

from pathlib import Path
from typing import cast
import json
import subprocess
import sys
import time
import urllib.parse
from course_backups import recent
from filter_csv import read_from_csv
from upload_csv import constants, get_access_token, bytesOrStrPrintable

def read_courses_from_file(filename: Path) -> tuple[list[int], list[str]]:
    """Takes the name of a CSV file containing course records (as from a
    Canvas provisioning report).  Returns a tuple for which the first element
    is the list of course ID numbers, and the second element is the list of
    course names (effectively shortnames)."""
    courses: list[dict] = read_from_csv(filename)
    numbers: list[int] = cast(list[int], [crs['canvas_course_id'] for crs in courses])
    names: list[str] = [crs['course_id'] for crs in courses]
    return numbers, names

def find_quiz_numbers(course_IDs: list[int]) -> list[int]:
    assert len(course_IDs) > 0
    quizzes: list[int] = []
    token = get_access_token()

    for id in course_IDs:
        cmd = ['curl', '--no-progress-meter', '--show-error', 
                '--header', 'Authorization: Bearer ' + token,
                'https://{0}/api/v1/courses/{1}/quizzes'.format(constants()['host'], id) +
                '?search_term=information-fluency']
        print(cmd)
        output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
        data: list[dict] = json.loads(output)
        if len(data) > 1:
            raise Exception('ERROR: course {0} has {1} info-fluency quizzes.  Data\n\t{2}'.format(id, len(data), data))
        #print(id, data)
        if len(data) == 0:
            quizzes.append(0)
        else:
            quizzes.append(data[0]['id'])

    assert len(quizzes) == len(course_IDs)
    return quizzes

def get_report_status(course: int, quiz: int) -> list[dict]:
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
                '--header', 'Authorization: Bearer ' + token,
                'https://{0}/api/v1/courses/{1}/quizzes/{2}/reports'.format(constants()['host'], course, quiz)]
    print(cmd)
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    data: list[dict] = json.loads(output)
    return data

def get_one_report_status(course: int, status: dict) -> dict:
    assert 'quiz_id' in status, str(status)
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
                '--header', 'Authorization: Bearer ' + token,
                'https://{0}/api/v1/courses/{1}/quizzes/{2}/reports/{3}'.format(constants()['host'], 
                                                                                course, status['quiz_id'], 
                                                                                status['id'])]
    print(cmd)
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    data: dict = json.loads(output)
    return data 

def start_report(course: int, old_status: dict)-> dict:
    token = get_access_token()
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', 
            '--header', 'Authorization: Bearer ' + token,
            '--form', 'quiz_report[report_type]=' + old_status['report_type'],
            'https://{0}/api/v1/courses/{1}/quizzes/{2}/reports'.format(constants()['host'],
                                                                    course, old_status['quiz_id'])]
    print(cmd)
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    #print(output)
    data = json.loads(output)
    return data

def get_report(course: int, status: dict) -> str:
    # First, check if the report is available
    delay = 12
    max_tries = 50
    tries = 0    
    
    while 'file' not in status:
        tries += 1
        if tries > max_tries:
            raise Exception("Maximum tries exceeded")
        time.sleep(delay)
        status = get_one_report_status(course, status)
    
    # The report is now ready
    urlparts = urllib.parse.urlparse(status['file']['url'])
    queryparts = urllib.parse.parse_qs(urlparts.query)
    url = urllib.parse.urlunparse([urlparts.scheme, urlparts.netloc, urlparts.path, '',
                                  'verifier=' + queryparts['verifier'][0], ''])
    token = get_access_token()
    cmd = ['curl', '--no-progress-meter', '--show-error', '--location',
           '--header', 'Authorization: Bearer ' + token, url]
    print(cmd)
    output: str = bytesOrStrPrintable(subprocess.check_output(cmd))
    # chunks = output.split('\n')
    # for i in range(len(chunks)):
    #     print(chunks[i])
    return output

def write_report(contents: str, fname: str, outputdir: Path) -> None:
    with open(outputdir.joinpath(fname), 'w') as f:
        f.write(contents)

def create_reports(course_IDs: list[int], course_names: list[str], quizzes: list[int], outputdir: Path) -> None:
    """Takes a list of numeric course ID's, a list of course names, and the directory
    in which to create the output files, and creates student and item reports
    for the info-literacy quizzes in those courses."""
    # Pre:
    assert len(course_IDs) > 0 and len(course_IDs) == len(course_names) == len(quizzes)
    
    # print(quizzes)
    course_stem = 'FYS'
    if course_names[0].startswith('SSS'):
        course_stem = 'SSS'

    student_report = ''
    item_report = ''
    for i in range(4): #(len(course_IDs)):
        if quizzes[i] == 0:
            continue
        else:
            quiz_status: list[dict] = get_report_status(course_IDs[i], quizzes[i])
            assert len(quiz_status) == 2
            for status in quiz_status:
                #print(course_IDs[i], status)
                newstat = status # To avoid assigning to status if we start a new report
                if 'file' not in status or not recent(status['file']['updated_at']):
                    print('Starting', status['readable_type'], 'report for quiz', status['quiz_id'])
                    newstat = start_report(course_IDs[i], status)
                report = get_report(course_IDs[i], newstat)
                if newstat['report_type'] == 'student_analysis':
                    # if len(student_report) > 0:
                    #     report = report[1:]
                    # student_report += '\n'.join(report)
                    student_report += report
                else:
                    # if len(item_report) > 0:
                    #     report = report[1:]
                    # item_report += '\n'.join(report)
                    item_report += report
    write_report(student_report, course_stem + '_students.csv', outputdir)        
    write_report(item_report, course_stem + '_items.csv', outputdir)        
                
                    


def main(argv: list[str]) -> int:
    most_recent_fall = 'Fall_2022'
    info_lit_dir = Path.home().joinpath('Documents', 'DEd', 'info-literacy', most_recent_fall)
    SSS_courses = read_courses_from_file(info_lit_dir.joinpath('SSS-courses.csv'))
    #print(SSS_courses)
    #print(list(zip(SSS_courses[0], SSS_courses[1])))
    quizzes: list[int] = find_quiz_numbers(SSS_courses[0])
    create_reports(SSS_courses[0], SSS_courses[1], quizzes, info_lit_dir)

    FYS_courses = read_courses_from_file(info_lit_dir.joinpath('FYS-courses.csv'))
    #print(FYS_courses)


    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))