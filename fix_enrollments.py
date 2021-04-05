#! /usr/bin/python3

# Filter to add training-course enrollments to enrollments.csv
# Peter Brown <peter.brown@converse.edu>, 2020-07-31

import re
from typing import Dict, List, Set, Tuple

def filter_enrollments(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    outrecords:List[Dict[str, str]] = []
    course_subs:Dict[str, str] = { "PSY100.95-2021-FA" : "PSY100.95A-2021-FA" }
    course_doubles:Dict[str,str] = { "BIO309H.01-2021-JA": "BIO309.01-2021-JA",
                                     "PSY281H.95-2021-JA": "PSY281.95-2021-JA" }
    blacklist:Tuple[Tuple[str,str], ...] = (#('1412633', 'EDU299H.01-2021-JA'),
                                            #('1412633', 'ENG299H.01-2021-JA'),
                                            ('1531377', 'CHM203L.02-2021-SP'),
                                            ('1504003', 'CHM203L.02-2021-SP'),
                                            ('1508775', 'CHM203L.01-2021-SP'),
                                            ('1528718', 'CHM203L.01-2021-SP'),
                                            ('1524907', 'CHM203L.01-2021-SP'),
                                            ('1346473', 'ENG525.S1-2021-SP'),
                                            ('1563361', 'EDU592.Y6-2021-SP'),
                                            ('1564738', 'EDU592.Y1-2021-AS'))
    students:Set(str) = set()
    teachers:Set(str) = set()
    for record in inrecords:
        # Massage record itself
        if record['course_id'] in course_subs.keys():
            record['course_id'] = course_subs[record['course_id']]
        elif record['course_id'] in course_doubles.keys():
            newrecord = dict(record,
                             course_id=course_doubles[record['course_id']])
            inrecords.append(newrecord)

        # Add the adjusted record to outrecords
        if not (record['user_id'], record['course_id']) in blacklist:
            outrecords.append(record)

        # Keep track of students and teachers
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
        record = {'course_id': 'C@C', 'root_account': '', 'user_id': s,
                  'user_integration_id': '', 'role': 'observer',
                  'section_id': '', 'status': 'active',
                  'associated_user_id': '', 'limit_section_priveleges': ''}
        outrecords.append(record)

    for t in teachers:
        record:Dict[str, str] = {'course_id': 'growing_with_canvas',
                                 'root_account': '', 'user_id': t, 'user_integration_id': '',
                                 'role': 'student', 'section_id': '','status': 'active',
                                 'associated_user_id': '', 'limit_section_priveleges': '' }
        outrecords.append(record)
        record = {'course_id': 'C@C', 'root_account': '', 'user_id': t,
                  'user_integration_id': '', 'role': 'observer',
                  'section_id': '', 'status': 'active',
                  'associated_user_id': '', 'limit_section_priveleges': ''}
        outrecords.append(record)
                                 
    return outrecords
