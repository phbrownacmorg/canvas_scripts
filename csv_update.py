#! /usr/bin/python3

# Filter to correct the case of course fullnames for import to Canvas.
# Input comes from one CSV file, and output is written to another.
# Peter Brown <peter.brown@converse.edu>, 2020-08-04

from pathlib import Path
import sys
from filter_csv import filter_csv, stem_list
from upload_csv import get_last_upload, write_last_upload, upload

# ------------------- filtering ----------------------------------------

# Returns a dict of the infile and outfile directories
def get_data_dirs() -> dict[str, Path]:
    all_paths = {'linux': {'inputdir': Path('/mnt').joinpath('Canvas_Data'),
                           'outputdir': Path.home().joinpath('bin',
                                                             'canvas_scripts')},
                 'win32': {'inputdir': Path('//speed-server/Canvas_Data'),
                           'outputdir': Path.home().joinpath('Desktop',
                                                             'canvas_scripts')}}
    return all_paths[sys.platform]

## ----- uploading --------------------------------------------------

def main(argv:list[str]) -> int:
    filters = stem_list()
    datadirs:dict[str, Path] = get_data_dirs()
    try:
        last_upload:int = get_last_upload(datadirs['outputdir'])

        do_filtering:bool = True
        if len(argv) > 1 and argv[1] == '--upload-only':
            do_filtering = False
        # print(argv, do_filtering)
   
        for stem in filters.keys():
            print(stem)
            if do_filtering:
                print('Filtering...')
                filter_csv(stem, datadirs, filters[stem])
            last_upload = upload(stem, datadirs['outputdir'], last_upload)
    except RuntimeError as e:
        #print('RuntimeError:', e.args[0])
        write_last_upload(e.args[0], datadirs['outputdir'])
        raise RuntimeError(e)
    else:    
        write_last_upload(str(last_upload), datadirs['outputdir'])
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
