
# Filter to correct the case of course fullnames for import to Canvas.
# Peter Brown <peter.brown@converse.edu>, 2020-07-15
# Infilename argument added, 2020-07-27
# get_data_dirs function added, 2020-07-31
# Changed from a standalone program to a library, 2020-08-04

#from pathlib import Path
from typing import cast

goodterms: tuple[str,...] = ('2021-SF', '2021-FA', '2021-JS',
                            '2021-JA', '2021-SP', '2021-AS',
                            '2021-BS', '2021-2S', '2021-3S',
                            '2122-FA', '2122-JA', '2122-SP',
                            '2122-AS', '2122-BS', '2122-2S', '2122-S3',
                            '2223-FA', '2223-JA', '2223-SP',
                            '2223-AS', '2223-BS', '2223-2S', '2223-3S',
                            '2324-SF', '2324-FA', '2324-JA',
                            '2324-JS', '2324-SP', '2324-AS',
                            '2324-BS', '2324-2S', '2324-3S',
                            '2425-FA', '2425-JA', '2425-SP',
                            '2425-AS', '2425-BS', '2425-2S',
                            '2526-FA', '2526-JA', '2526-SP')

# Make the course's long name a little easier on the eyes than the
# all-upper-case favored by the Registrar's Office.
def correct_long_name(coursename: str) -> str:
    downcased_words = ('a', 'an', 'at', 'by', 'for', 'in', 'of', 'on',
                       'to', 'up', 'and', 'as', 'but', 'or', 'nor')  
    upcased_words = ('2-D', '3-D', '3D', 'BA', 'BFA', 'CAD', 'CW', 'DHH', 'DIS',
                     'EC', 'ECE', 'ESL', 'HPE', 'HS', 'ID', 'II', 'III', 'IV',
                     'IX', 'LA', 'LD', 'MIDI', 'MFT', 'MS', 'NATO', 'R2S', 'SP',
                     'WWI', 'WWII')
    upcased_words_colons = ('DIS:', 'FYS:', 'HR:', 'II:', 'LA:', 'PD:', 'SP:')
    replacements = { 'Intership' : 'Internship' }
    
    # Force proper splits
    coursename = coursename.replace('&', ' & ')
    splitchars: tuple[str, ...] = cast(tuple[str, ...], (':', ','))
    for ch in splitchars:
        coursename = coursename.replace(ch, ch + ' ')
  
    wordlist = coursename.split()

    # Skip the first two words, which are the course prefix and number
    for i in range(2, len(wordlist)):
        # Usual case
        word: str = wordlist[i].capitalize()
        wordlist[i] = word

        if word in replacements.keys():
            wordlist[i] = replacements[word]

        # Now, handle the oddities.
        upperword: str = word.upper()
        lowerword: str = word.lower()

        if upperword in (upcased_words + upcased_words_colons):
            wordlist[i] = upperword

        # If a downcased word is first in the title, leave it capitalized
        elif i > 2 and lowerword in downcased_words:
            wordlist[i] = lowerword

        # "D/HH" is upcased regardless of context
        elif 'd/hh' in lowerword:
            wordlist[i] = word.replace('d/hh', 'D/HH').replace('D/hh', 'D/HH')
            
    return ' '.join(wordlist)

def adjust_account(account_id: str, course_id: str) -> str:
    result: str = account_id
    prefix: str = course_id[:3]
    if prefix == 'ATA':
        result = prefix
    return result

# Filter the record for one course, removing empty and NULL fields and
# correcting the case of the course long_name.
def filter_one_course(inrec: dict[str, str]) -> dict[str, str]:
    values_to_ignore = ['', 'NULL', '00:00.0']
    keys_to_ignore = ['course_format', 'blueprint_course_id']
    outrec: dict[str, str] = {}
    for key in inrec.keys():
        if key not in keys_to_ignore:
            value = inrec[key]
            if key == 'long_name':
                outrec['long_name'] = correct_long_name(value)
            elif key == 'account_id':
                outrec['account_id'] = adjust_account(value, inrec['course_id'])
            elif value not in values_to_ignore:
                outrec[key] = value
                #if key == 'status' and inrec['term_id'] not in goodterms:
                #    outrec['status'] = 'deleted'
            else:
                outrec[key] = ''
    return outrec

# Determine whether the course represented by RECORD should be entered
# in Canvas or not.
def valid_course(record: dict[str,str]) -> bool:
    result:bool = (record['term_id'] in goodterms)
    return result

# Takes a list of course records, each one a dictionary, filters them,
# and returns the result of that filtering.
def filter_courses(inrecords: list[dict[str, str]]) -> list[dict[str, str]]:
    outrecords: list[dict[str, str]] = []
    rejected_courses: list[str] = []
    for record in inrecords:
        if valid_course(record):
            outrecords.append(filter_one_course(record))
        else:
            rejected_courses.append(record['course_id'])
            #print('Course rejected: ', record['course_id'])
    print('Rejected:', rejected_courses)
    # Post:
    assert len(inrecords) - len(rejected_courses) == len(outrecords), \
        f"{len(inrecords)} - {len(rejected_courses)} != {len(outrecords)}"
    return outrecords
