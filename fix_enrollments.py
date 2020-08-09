#! /usr/bin/python3.8

# Filter to add training-course enrollments to enrollments.csv
# Peter Brown <peter.brown@converse.edu>, 2020-07-31

import re
from typing import Dict, List

def filter_enrollments(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    outrecords:List[Dict[str, str]] = []
    students = set()
    teachers = set()
    for record in inrecords:
        outrecords.append(record)
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
