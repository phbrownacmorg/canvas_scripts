#! /usr/bin/python3

# Functions for performing course backups

from pathlib import Path
import csv
import subprocess
import sys
from filter_csv import read_from_csv
from upload_csv import constants, get_access_token, bytesOrStrPrintable

def print_courses(courses: list[dict]) -> None:
    for course in courses:
        print(course['canvas_course_id'], course['course_id'], course['status'])

def read_course_list(term: str) -> list[int]:
    reportsdir = Path.home().joinpath('Documents', 'DEd', 'Canvas', 'course_backups', 'reports')
    print(reportsdir)
    courses: list[dict] = read_from_csv(reportsdir.joinpath(term + '-courses.csv'))
    courses = list(filter(lambda c: c['status'] == 'active', courses))

    xlist: list[dict] = read_from_csv(reportsdir.joinpath(term + '-xlist.csv'))

    print_courses(courses)
    result: list[int] = []


    return result


def main(argv: list[str]) -> int:
    term: str = '2223-SP'
    courselist: list[int] = read_course_list(term)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
