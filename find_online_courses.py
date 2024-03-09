from pathlib import Path
from typing import Any, cast
import argparse
import json
import sys
import time
from read_courses import read_course_list
from filter_csv import write_outfile


def parse_args(argv: list[str]) -> dict[str,Any]:
    parser = argparse.ArgumentParser(prog='find_online_courses.py')
    parser.add_argument('--term', default='',
                        help='Term to for which to list online courses (default all terms)')
    args = parser.parse_args(argv)
    return vars(args)

def online(course_id: str) -> bool:
    return '.9' in course_id or '.UC9' in course_id or '.E9' in course_id or '.M9' in course_id 

def hybrid(course_id: str) -> bool:
    return '.Y' in course_id or '.Z' in course_id

def undergraduate(course_id: str) -> bool:
    return course_id[3] < '5'

def main(argv: list[str]) -> int:
    args: dict[str,Any] = parse_args(argv[1:])
    print(args, flush=True)
    term: str = args['term']

    backups_dir = Path.home().joinpath('Documents', 'DEd', 'course_backups')
    
    courselist: list[dict[str,Any]] = read_course_list(term, Path.joinpath(backups_dir, 'reports'))
    print(len(courselist), 'courses')
    # print_courses(courselist)

    print(time.asctime(), flush=True)

    onlines: list[dict[str, Any]] = [c for c in courselist if online(c['course_id']) and undergraduate(c['course_id'])]
    print('onlines:', len(onlines))
    hybrids: list[dict[str, Any]] = [c for c in courselist if hybrid(c['course_id']) and undergraduate(c['course_id'])]
    print('hybrids', len(hybrids))

    all = onlines + hybrids
    all = sorted(all, key=lambda elt: elt['course_id'])
    if len(hybrids) > 0:
        all = sorted(all, key=lambda elt: elt['course_id'][elt['course_id'].rfind('.'):])
    all = sorted(all, key=lambda elt: elt['term_id'])

    if len(term) > 0:
        term = term + '-'
    write_outfile(all, Path.joinpath(backups_dir, 'reports', term+'online_hybrid.csv'))

    print(time.asctime(), flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
