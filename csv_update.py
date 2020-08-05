#! /usr/bin/python3.8

# Filter to correct the case of course fullnames for import to Canvas.
# Input comes from one CSV file, and output is written to another.
# Peter Brown <peter.brown@converse.edu>, 2020-08-04

from pathlib import Path
import sys
from typing import Dict, List
from filter_csv import filter, stem_list
from upload_csv import upload

# ------------------- filtering ----------------------------------------

# Returns a dict of the infile and outfile directories
def get_data_dirs() -> Dict[str, Path]:
    all_paths = {'linux': {'inputdir': Path('/mnt').joinpath('Canvas_Data'),
                           'outputdir': Path.home().joinpath('bin',
                                                             'canvas_scripts')},
                 'win32': {'inputdir': Path('//speed-server/Canvas_Data'),
                           'outputdir': Path.home().joinpath('Desktop',
                                                             'canvas_scripts')}}
    return all_paths[sys.platform]

## ----- uploading --------------------------------------------------

def main(argv:List[str]) -> int:
    filters = stem_list()
    last_upload = 0
    for stem in ['users']: #filters.keys():
        filter(stem, get_data_dirs(), filters[stem])
        # Upload
        last_upload = upload(stem, get_data_dirs()['outputdir'], last_upload)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

