import datetime as dt
from zoneinfo import ZoneInfo

good_suffixes = ('FA', 'JA', 'SP', 'AS', 'BS', '2S', '3S')

def good_term(term_id: str) -> bool:
    """Return True if TERM_ID is a term to be imported to Canvas, and
       False otherwise.  At the moment, the only test applied is
       whether TERM_ID ends with a suffix corresponding to a term we
       put into Canvas."""
    return term_id[-2:] in good_suffixes

def read_date(datespec: str) -> dt.datetime:
    """Extract a date from the kind of string found in Jenzabar date
       specifications."""
    spec = datespec
    if spec[0] == "'":
        spec = spec[1:]
    date = dt.datetime.fromisoformat(spec).replace(tzinfo=ZoneInfo('America/New_York'))
    # print(date)
    return date

def filter_one_term(inrec: dict[str, str]) -> list[dict[str, str]]:
    """Takes a single term INREC and returns the list of term
       specifications corresponding to that term."""
    outrecords: list[dict[str, str]] = []
 
    # Extract the basics
    term_id = inrec['term_id']
    suffix = term_id[-2:]       # Suffix indicating which term this is
    start = read_date(inrec['start_date'])
    csv_end = read_date(inrec['end_date'])

    # *Actual* course end
    end = csv_end + dt.timedelta(days = 1)  # Because the time is 00:00:00, needs to be the day *after*
    if suffix in ('FA', 'SP'):              # In long terms,
        end = end + dt.timedelta(days = 7)  #   move to the end of exams (a week later)
    
    # Time to open courses to students
    student_start = start + dt.timedelta(days = -5) # Good for summer terms
    if suffix == 'SP':
        student_start = start + dt.timedelta(days = -start.isoweekday()) # Preceding Sunday
    elif suffix == 'FA':
        student_start = start + dt.timedelta(days = -start.isoweekday() - 4)  # Preceding Wednesday
    elif suffix == 'JA':
        student_start = start.replace(day = 1, month = 1) # Always Jan. 1

    # Time to close courses
    faculty_close = end + dt.timedelta(days = 7)    # Grades are commonly due a week or so after end of term
    student_close = end + dt.timedelta(days = 6)    # Faculty *will* accept late work until the last moment,
                                                    #   even if theyr're not supposed to.
    
    
    # Initial record
    outrecords.append({ 'term_id': term_id,
                        'name': inrec['name'],
                        'status': inrec['status'],
                        'date_override_enrollment_type': '',
                        'start_date': "'" + start.isoformat(' '),
                        'end_date': "'" + end.isoformat(' ')
                    })
    # Faculty record
    outrecords.append({ 'term_id': term_id,
                        'name': inrec['name'],
                        'status': inrec['status'],
                        'date_override_enrollment_type': 'TeacherEnrollment',
                        'start_date': "",
                        'end_date': faculty_close.isoformat(' ')
                    })
    # Student record
    outrecords.append({ 'term_id': term_id,
                        'name': inrec['name'],
                        'status': inrec['status'],
                        'date_override_enrollment_type': 'StudentEnrollment',
                        'start_date': student_start.isoformat(' '),
                        'end_date': student_close.isoformat(' ')
                    })

    return outrecords
    
def filter_terms(inrecords: list[dict[str,str]]) -> list[dict[str,str]]:
    """Takes a list of term specifications INRECORDS and returns a
       filtered list of term specifications for import to Canvas."""
    outrecords: list[dict[str, str]] = []
    for record in inrecords:
        if good_term(record['term_id']):
            outrecords.extend(filter_one_term(record))
    return outrecords

def main(args: list[str]) -> int:
    """For testing purposes."""
    assert good_term('2526-FA') and good_term('2526-SP') and \
        good_term('2526-AS') and good_term('2526-BS') and \
        good_term('2526-2S') and good_term('2526-JA'), 'Good terms called bad'
    assert not (good_term('2526-JS') or good_term('2526-SF')), \
        'Bad terms called good'

    import filter_csv as fc
    from pathlib import Path
    infile = Path(__file__).parent.joinpath('terms_in.csv')
    assert infile.is_file()
    inrecords = fc.read_from_csv(infile)
    # print(inrecords)
    assert len(inrecords) > 0

    first_out = filter_one_term(inrecords[5])
    print(first_out)

    print(filter_terms(inrecords))

    return 0
    
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

