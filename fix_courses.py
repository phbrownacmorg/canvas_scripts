#! /usr/bin/python3.8

# Filter to correct the case of course fullnames for import to Canvas.
# Peter Brown <peter.brown@converse.edu>, 2020-07-15
# Infilename argument added, 2020-07-27
# get_data_dirs function added, 2020-07-31
# Changed from a standalone program to a library, 2020-08-04

from typing import Dict, List, Tuple

# Make the case of coursename a little easier on the eyes than the
# all-upper-case favored by the Registrar's Office.
def correct_case(coursename:str) -> str:
    downcased_words = ('a', 'an', 'at', 'by', 'for', 'in', 'of', 'on',
                       'to', 'up', 'and', 'as', 'but', 'or', 'nor')  
    upcased_words = ('2-D', '3-D', '3D', 'BA', 'BFA', 'CAD', 'CW', 'DHH', 'DIS',
                     'EC', 'ECE', 'ESL', 'HPE', 'HS', 'ID', 'II', 'III', 'IV',
                     'LA', 'LD', 'MIDI', 'MFT', 'MS', 'NATO', 'R2S', 'SP')
    upcased_words_colons = ('DIS:', 'FYS:', 'HR:', 'II:', 'LA:', 'PD:', 'SP:')
    upcased_words_nocontext = ('D/HH')
    
    # Force proper splits
    coursename = coursename.replace('&', ' & ')
    splitchars:str = (':', ',')
    for ch in splitchars:
        coursename = coursename.replace(ch, ch + ' ')
  
    wordlist = coursename.split()

    # Skip the first two words, which are the course prefix and number
    for i in range(2, len(wordlist)):
        # Usual case
        word:str = wordlist[i].capitalize()
        wordlist[i] = word

        # Now, handle the oddities.
        upperword:str = word.upper()
        lowerword:str = word.lower()

        if upperword in (upcased_words + upcased_words_colons):
            wordlist[i] = upperword

        # If a downcased word is first in the title, leave it capitalized
        elif i > 2 and lowerword in downcased_words:
            wordlist[i] = lowerword

        # "D/HH" is upcased regardless of context
        elif 'd/hh' in lowerword:
            wordlist[i] = word.replace('d/hh', 'D/HH').replace('D/hh', 'D/HH')
            
    return ' '.join(wordlist)

goodterms:Tuple[str,...] = ('2021-SF', '2021-FA', '2021-JS',
                            '2021-JA', '2021-SP', '2021-AS',
                            '2021-BS', '2021-2S', '2021-3S')

# Filter the record for one course, removing empty and NULL fields and
# correcting the case of the course long_name.
def filter_one_course(inrec:Dict[str, str]) -> Dict[str, str]:
    values_to_ignore = ['', 'NULL', '00:00.0']
    keys_to_ignore = ['course_format', 'blueprint_course_id']
    outrec:Dict[str, str] = {}
    for key in inrec.keys():
        if key not in keys_to_ignore:
            value = inrec[key]
            if key == 'long_name':
                outrec['long_name'] = correct_case(value)
            elif value not in values_to_ignore:
                outrec[key] = value
                #if key == 'status' and inrec['term_id'] not in goodterms:
                #    outrec['status'] = 'deleted'
            else:
                outrec[key] = ''
    return outrec

# Determine whether the course represented by RECORD should be entered
# in Canvas or not.
def valid_course(record:Dict[str,str]) -> bool:
    result:bool = (record['term_id'] in goodterms)
    return result

# Takes a list of course records, each one a dictionary, filters them,
# and returns the result of that filtering.
def filter_courses(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    outrecords:List[Dict[str, str]] = []
    for record in inrecords:
        if valid_course(record):
            outrecords.append(filter_one_course(record))
    return outrecords
