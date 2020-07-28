#! /usr/bin/python3.7

# Filter to correct the case of course fullnames for import to Canvas.
# Input comes from one CSV file, and output is written to another.
# Peter Brown <peter.brown@converse.edu>, 2020-07-15
# Infilename argument added, 2020-07-27

import csv
from pathlib import Path
import re
from typing import Dict, List

# Reads the CSV file into a list of dictionaries, one dictionary per
# row of data in the CSV file.  For each row, the keys of the dict are
# the CSV column titles, and the values are the corresponding data
# values from the row.
def read_from_csv(infile:Path) -> List[Dict[str, str]]:
    records:List[Dict[str, str]] = []
    with open(infile, newline='') as f:
        reader = csv.DictReader(f) # Turns each row into a dictionary
        for row in reader:
            records.append(row)
    # Post: for all 0 <= i < j < len(records),
    #              records[i].keys() == records[j].keys()
    # The DictReader guarantees this is true, BTW.
    return records

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
            else:
                outrec[key] = ''
    return outrec

def filter_records(inrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    outrecords:List[Dict[str, str]] = []
    for record in inrecords:
        outrecords.append(filter_one_course(record))
    return outrecords

def write_outfile(records:List[Dict[str, str]], outfile:Path) -> None:
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        for row in records:
            writer.writerow(row)

def main(argv:List[str]) -> int:
    infile:Path = Path('courses.csv')
    if len(argv) > 1:
        infile = Path(argv[1])
    inrecords:List[Dict[str, str]] = read_from_csv(infile)
    outrecords:List[Dict[str, str]] = filter_records(inrecords)
    #print(outrecords)
    outfile:Path = infile.with_name(infile.stem + '-fixed.csv')
    write_outfile(outrecords, outfile)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
