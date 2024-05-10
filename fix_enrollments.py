#! /usr/bin/python3

# Filter to add training-course enrollments to enrollments.csv
# Peter Brown <peter.brown@converse.edu>, 2020-07-31

import re
from typing import Dict, List, Set, Tuple

def ok_to_add(inrecord:Dict[str, str], last_outrecord:Dict[str, str]) -> bool:
    # blacklist simply removes a given person's enrollments in a given course
    # from automatic processing.  From there, the desired result can be
    # produced manually, without having it overwritten by the automatic
    # process.  (Note that Canvas does *not* take any action if an enrollment
    # is simply missing from the automatic enrollment list.)
    blacklist:List[Tuple[str,str], ...] = \
        [ #('1412633', 'EDU299H.01-2021-JA'),
          #('1412633', 'ENG299H.01-2021-JA'),
          #('1531377', 'CHM203L.02-2021-SP'),
          #('1504003', 'CHM203L.02-2021-SP'),
          #('1508775', 'CHM203L.01-2021-SP'),
          #('1528718', 'CHM203L.01-2021-SP'),
          #('1524907', 'CHM203L.01-2021-SP'),
          #('1346473', 'ENG525.S1-2021-SP'),
          #('1563361', 'EDU592.Y6-2021-SP'),
          #('1564738', 'EDU592.Y1-2021-AS'),
          #('1524391', 'EDU378.S1-2021-AS'),
          #  ('1083562', 'ART314.95-2122-FA'),
          # ('1083562', 'ART501.95-2122-FA')
          #  ('1522966', 'EDU304.01-2122-SP'),
          #  ('1520119', 'EDU619B.E95-2122-SP')
          #  ('1526865', 'ART300.01-2223-SP'),
          #  ('1511583', 'CHM315L.01-2223-SP'),
          #  ('1536013', 'ECN201.01-2223-SP'),
          #  ('1294527', 'ECN202.01-2223-SP'),
          #  ('1563113', 'ACC211.01-2223-SP'),
          #  ('1569305', 'EDU591.YB-2223-JA')
          #  ('1569583', 'EDU592.Y8-2223-SP'),
          #  ('1528694', 'DES382.95-2223-SP'),
          #  ('1570779', 'EDU592.Y5-2223-SP')
          #  ('1530067', 'ART501.97-2223-BS'),
          #  ('1192472', 'PLP835.UC9-2223-BS')
            ('1277493', 'SED390.02-2324-SP'),
            ('1535530', 'PSY480.01-2324-SP'),
            ('1530207', 'PSY480.01-2324-SP')
        ]

    result:bool = not ((inrecord['user_id'], inrecord['course_id']) in blacklist)

    # Suppress active/inactive pairs
    if result and (inrecord['status'] == 'inactive') \
       and (last_outrecord['status'] == 'active') \
       and (inrecord['user_id'] == last_outrecord['user_id']) \
       and (inrecord['course_id'] == last_outrecord['course_id']):
        result = False

    return result


def filter_enrollments(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    #print('Filtering enrollments')
    outrecords:List[Dict[str, str]] = []
    # Track the last record added to the outrecords
    last_outrecord = {'status': None}
    
    # course_subs is used to substitute one course for another.  The effect is
    # basically the same as cross-listing.
    course_subs:Dict[str, str] = { "PSY100.95-2021-FA" : "PSY100.95A-2021-FA" }

    # course_doubles, a set of key-value pairs, is used to force anyone
    # enrolled in the "key" course to also be enrolled in the "value" course,
    # with the same role.
    course_doubles:Dict[str,str] = { "BIO309H.01-2021-JA": "BIO309.01-2021-JA",
                                     "PSY281H.95-2021-JA": "PSY281.95-2021-JA"}
    
    students:Set(str) = set()
    teachers:Set(str) = set()
    #print(blacklist[0][0])
    for record in inrecords:
        # Massage record itself
        if record['course_id'] in course_subs.keys():
            record['course_id'] = course_subs[record['course_id']]
        elif record['course_id'] in course_doubles.keys():
            newrecord = dict(record,
                             course_id=course_doubles[record['course_id']])
            inrecords.append(newrecord)

        # Add the adjusted record to outrecords
        #if not (record['user_id'], record['course_id']) in blacklist:
        if ok_to_add(record, last_outrecord):
            #if record['user_id'] == blacklist[0][0]:
            #    print(record)
            outrecords.append(record)
            last_outrecord = record

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
