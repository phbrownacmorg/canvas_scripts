# Library to support reading courses and fixing course names.
# This library is separate from fix_courses to avoid a circular import for read_from_csv

from typing import Any
from pathlib import Path
from filter_csv import read_from_csv

def print_course(course: dict[str, Any], endstr: str = '\n') -> None:
    print(course['canvas_course_id'], course['course_id'], course['status'], end=endstr, flush=True)

def print_courses(courses: list[dict[str, Any]]) -> None:
    for course in courses:
        print_course(course)

def make_course_id(id_list: list[str]) -> str:
    assert len(id_list) > 1 # Must be at least two ID's
    # Extract the term (with its leading hyphen) from the first course
    term = id_list[0][-8:]
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
    return result + term

def fix_course_ids(courselist: list[dict[str, Any]], xlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coursedict: dict[str, dict[str, Any]] = {}
    # Put the courses in a dictionary for quick reference
    # Is there a faster way to do this?
    for c in courselist:  
        coursedict[c['course_id']] = c

    # Iterate over the xlists, adjusting the courses as needed
    i = 0
    xlist = sorted(xlist, key=lambda elt: elt['nonxlist_course_id'])
    xlist = sorted(xlist, key=lambda elt: elt['xlist_course_id'])
    ids: list[str] = []
    while i < len(xlist):
        host_id = xlist[i]['xlist_course_id']
        if len(ids) == 0:
            ids.append(host_id)
        guest_id = xlist[i]['nonxlist_course_id']
        #ids.append(guest_id)
        try:
            assert coursedict[host_id]['course_id'] == '' or coursedict[host_id]['course_id'][-7:] == coursedict[guest_id]['course_id'][-7:], \
                f"Cross-term cross-listing: {coursedict[host_id]['course_id']} <- {coursedict[guest_id]['course_id']}"
            coursedict[guest_id]['status'] = host_id # guest courses are never active
        except KeyError as e:
            print('KeyError:', e, 'not found: wrong term?')
        except AssertionError as e:
            print(e)
        else:
            ids.append(guest_id)

        # CONSIDER using the numeric ids for comparisons like this
        # If the next xlist line refers to the same host course, we're not done
        # accumulating ids.        
        if (i == len(xlist) - 1) or (xlist[i+1]['xlist_course_id'] != host_id):
            if len(ids) > 1:
                coursedict[host_id]['course_id'] = make_course_id(ids)
            ids = []
        i += 1
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

# def set_division(courselist: list[dict[str, Any]]) -> list[dict[str, Any]]:
#     for c in courselist:
#         # First digit of the course number
        

def read_course_list(term: str, reportsdir: Path) -> list[dict[str, Any]]:
    if len(term) > 0:
        term = term + '-'
    courses: list[dict[str, Any]] = read_from_csv(reportsdir.joinpath(term + 'courses.csv'))
    xlist: list[dict[str, Any]] = read_from_csv(reportsdir.joinpath(term + 'xlist.csv'))
    courses = fix_course_ids(courses, xlist)
    courses = set_modality(courses)
    courses = [c for c in courses if c['status'] == 'active'] # Filter out any courses that were not published
    return courses
