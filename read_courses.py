# Library to support reading courses and fixing course names.
# This library is separate from fix_courses to avoid a circular import for read_from_csv

from typing import Any, cast
from pathlib import Path
from filter_csv import read_from_csv
import re

def print_course(course: dict[str, Any], endstr: str = '\n') -> None:
    print(course['canvas_course_id'], course['course_id'], course['status'], end=endstr, flush=True)

def print_courses(courses: list[dict[str, Any]]) -> None:
    for course in courses:
        print_course(course)

def valid_course(course: dict[str, Any]) -> bool:
    return len(course['course_id']) > 0 and len(course['term_id']) > 0

def make_course_id(id_list: list[str]) -> str:
    id_list = [id for id in id_list if len(id) > 0]
    assert len(id_list) > 1 # Must be at least two ID's
    # Extract the term (with its leading hyphen) from the first course
    term = id_list[0][-8:]
    assert len(term) == 8, 'No term on first id'
    # Remove all the terms
    id_list = list(map(lambda elt: elt[:-8], id_list))
    id_list.sort() # Ensure that common prefixes happen together

    result = id_list[0]
    prefix = result[:3]
    for i in range(1, len(id_list)):
        if id_list[i][:3] == prefix:
            result = result + '/' + id_list[i][3:]
        else:
            result = result + '/' + id_list[i]
            prefix = id_list[i][:3]

    assert len(result) > 0, 'Empty result'
    return result + term

def fix_course_ids(courselist: list[dict[str, Any]], xlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # First: for any courses without course_id but *with* a workable shortname, fill in the course_id.
    for c in courselist:
        if c['course_id'] == '' and len(c['short_name']) > 0:
            c['course_id'] = c['short_name']
    courselist = list(filter(valid_course, courselist))

    coursedict: dict[int, dict[str, Any]] = {}
    # Put the courses in a dictionary for quick reference
    # Is there a faster way to do this?
    for c in courselist:  
        coursedict[c['canvas_course_id']] = c

    # Iterate over the xlists, adjusting the courses as needed
    i = -1 # So the i += 1 in the loop happens just once
    xlist = sorted(xlist, key=lambda elt: elt['canvas_nonxlist_course_id'])
    xlist = sorted(xlist, key=lambda elt: elt['canvas_xlist_course_id'])
    ids: list[str] = []
    while i < (len(xlist) - 1):
        i += 1
        host_id: int = cast(int, xlist[i]['canvas_xlist_course_id'])
        if host_id not in coursedict:
            continue
        host_name: str = cast(str, coursedict[host_id]['course_id'])
        if host_name == '':  # Should not happen; these should have been filtered out previously
            continue
        elif len(ids) == 0:
            ids.append(host_name)
        guest_id: int = cast(int, xlist[i]['canvas_nonxlist_course_id'])
        if guest_id in coursedict:
            guest_name: str = cast(str, coursedict[guest_id]['course_id'])
            if len(guest_name) > 0 and host_name[-7:] == guest_name[-7:]:
                coursedict[guest_id]['status'] = host_name  # guest courses are never active
                ids.append(guest_name)

        # try:
        #     assert host_id[-7:] == guest_id[-7:], \
        #         f"Cross-term cross-listing: {host_id} <- {guest_id}"
        #     coursedict[guest_id]['status'] = host_id
        #     # Paranoia
        #     assert host_id == coursedict[host_id]['course_id']
        #     assert guest_id == coursedict[guest_id]['course_id']
        # except KeyError as e:
        #     print(f"KeyError: {e} not found: wrong term? '{host_id}' '{guest_id}'")
        # except AssertionError as e:
        #     print(e)
        # else:
        #     ids.append(guest_id)

        # CONSIDER using the numeric ids for comparisons like this
        # If the next xlist line refers to the same host course, we're not done
        # accumulating ids.        
        if (i == len(xlist) - 1) or (xlist[i+1]['xlist_course_id'] != host_id):
            # More than one id *and* the merging hasn't already been done
            if len(ids) > 1 and '/' not in coursedict[host_id]['course_id']:
                coursedict[host_id]['course_id'] = make_course_id(ids)
            ids = []
#    new_courselist = [c for c in coursedict.values() if c['course_id']
    return sorted(coursedict.values(), key=lambda elt: elt['course_id'])

def set_modality(courselist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for c in courselist:
        course_id: str = c['course_id']
        if '.9' in course_id or '.UC9' in course_id or '.E9' in course_id or '.M9' in course_id:
            c['modality'] = 'online'
        elif '.Y' in course_id or '.Z' in course_id:
            c['modality'] = 'hybrid'
        else:
            c['modality'] = 'face to face'
    return courselist

def set_division(courselist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specials: dict[str, str] = {'MUH-graduate-exams-2122-FA': 'G',
                                'MUH-graduate-exams-2021-FA': 'G'}
    num_RE = '(?P<num>[0-9]{3}[A-Z]?)'
    prefix_RE = '[A-Z]{3}(/[A-Z]{3})*'

    for i in range(len(courselist)):
        c = courselist[i]
        course_id = c['course_id']
        if course_id in specials:
            c['division'] = specials[course_id]
        else:
            assert len(course_id) > 6, f"No course_id: {c}"
            first_num = re.match(prefix_RE + num_RE, course_id)
            assert first_num is not None, f"'{c['course_id']}' ({i}) does not match '{prefix_RE + num_RE}'"
            num = first_num.group('num')
            assert num[0] in '012345678', f"'{c['course_id']}' yields subscriptable '{num}' ({prefix_RE + num_RE})"
            if num[0] in '01234':
                c['division'] = 'U'
            else:
                c['division'] = 'G'

            while '/' in course_id:
                course_id = course_id[course_id.find('/')+1:]
                first_num = re.match(num_RE, course_id)
                if not first_num:
                    first_num = re.match(prefix_RE + num_RE, course_id)
                assert first_num is not None, f"'{course_id}' does not match '{prefix_RE + num_RE}' ('{c['course_id']}')"
                num = first_num.group('num')
                assert num[0] in '012345678', f"'{c['course_id']}' yields '{num}'"
                if num[0] in '01234' and c['division'] == 'G':
                    c['division'] = 'U/G'
                elif num[0] in '5678' and c['division'] == 'U':
                    c['division'] = 'U/G'

    return courselist    

def read_course_list(term: str, reportsdir: Path) -> list[dict[str, Any]]:
    if len(term) > 0:
        term = term + '-'
    courses: list[dict[str, Any]] = read_from_csv(reportsdir.joinpath(term + 'courses.csv'))
    # Get rid of the courses with no terms or no course_id
    #courses = 
    # print_courses(courses)
    xlist: list[dict[str, Any]] = read_from_csv(reportsdir.joinpath(term + 'xlist.csv'))
    courses = fix_course_ids(courses, xlist)
    courses = [c for c in courses if c['status'] == 'active'] # Filter out any courses that were not published
    courses = set_modality(courses)
    courses = set_division(courses)

    return courses
