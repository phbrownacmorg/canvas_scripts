#! /usr/bin/python3.9

# Functions to filter Canvas attendance reports
# Peter Brown <peter.brown@converse.edu>, 2021-03-03

from pathlib import Path
import sys
from typing import Dict, List
from filter_csv import read_from_csv, write_outfile

destfile:Path = Path('/var/www/html/attendance/current-term.csv')
srcdir:Path = Path('/mnt/U/DEd/')

def is_csv_file(p:Path) -> bool:
    """Returns True iff P is a regular file with a .csv extension."""
    return p.is_file() and p.suffix == '.csv'

def newer_than(p:Path, mtime:float) -> bool:
    """Returns True iff the last-modified time of P is later than the given MTIME."""
    return p.stat().st_mtime > mtime

def find_input_files(mtime:float, indir:Path) -> List[Path]:
    """Returns a list of the .csv files in INDIR that are newer than MTIME."""
    newfiles:List[Path] = []
    for f in indir.iterdir():
        if is_csv_file(f) and newer_than(f, mtime):
            newfiles.append(f)
    return newfiles

def filter_attendance_record(inrec:Dict[str, str]) -> Dict[str, str]:
    """Filters an attendance record INREC and returns the result.  The
    filtering is mostly getting rid of unwanted fields."""
    outrec:Dict[str, str] = {}
    goodkeys:List[str] = ['Class Date', 'Course Code', 'Student Name',
                          'SIS Student ID','Attendance', 'Badges', 'Never showed',
                          'Teacher Name','Course Name','Section Name']
    for key in goodkeys:
        outrec[key] = inrec[key]
    return outrec

def attrec_key(rec:Dict[str, str]) -> str:
    """Extract and return a sorting key from an attendance record REC."""
    return rec['Class Date'] + rec['Course Code'] + rec['Student Name'] \
        + rec['SIS Student ID']

def merge_attendances(oldrecords:List[Dict[str, str]],
                      newrecords:List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Merges the attendance records in NEWRECORDS in with those in
    OLDRECORDS, and returns the result.  Neither NEWRECORDS nor
    OLDRECORDS is modified."""
    result:List[Dict[str, str]] = oldrecords[:]
    for rec in newrecords:
        outrec:Dict[str, str] = filter_attendance_record(rec)
        if outrec not in result:
            result.append(outrec)
    result.sort(key=attrec_key)
    return result
    
def main(argv:List[str]) -> int:
    """Looks in a globally-defined folder SRCDIR for .csv files with
    attendance data.  The data from the files in SRCDIR that are newer
    than the globally-defined file DESTFILE is merged in with the data
    already in DESTFILE, and the result written back to DESTFILE."""
    mtime:float = 0
    oldrecords:List[Dict[str, str]] = []
    newrecords:List[Dict[str,str]] = []
    if destfile.exists():
        oldrecords = read_from_csv(destfile)
        mtime = destfile.stat().st_mtime
    print(len(oldrecords))
    infiles:List[Path] = find_input_files(mtime, srcdir)
    #print(infiles)
    for f in infiles:
        print(f)
        newrecords.extend(read_from_csv(f))
        oldrecords = merge_attendances(oldrecords, newrecords)
    #print(oldrecords)
    if len(oldrecords) > 0: # Don't write anything if there are no records
        if destfile.exists(): # Only backup if there's a file to back up
            destfile.replace(destfile.with_suffix('.bak'))
        write_outfile(oldrecords, destfile)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

