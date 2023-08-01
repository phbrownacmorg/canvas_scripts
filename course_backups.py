#! /usr/bin/python3

# Functions for performing course backups

from pathlib import Path
import csv
import subprocess
import sys
from filter_csv import read_from_csv
from upload_csv import constants, get_access_token, bytesOrStrPrintable

def print_course(course: dict) -> None:
    print(course['canvas_course_id'], course['short_name'], course['status'])

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

def back_up_course(term: str, course: dict) -> None:
    pass

def main(argv: list[str]) -> int:
    term: str = '2223-SP'
    courselist: list[dict] = read_course_list(term)
    #print_courses(courselist)

    for c in courselist:
        print_course(c)
        back_up_course(term, c)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
