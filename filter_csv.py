#! /usr/bin/python3

# Functions to filter Canvas SIS CSV files prior to uploading them.
# Peter Brown <peter.brown@converse.edu>, 2020-08-04

import csv
from pathlib import Path
import sys
from typing import Callable
from fix_users import filter_users
from fix_courses import filter_courses
from fix_enrollments import filter_enrollments

# Almost-empty filter just returns a shallow copy of the input.
def identity_filter(records: list[dict[str, str]]) -> list[dict[str, str]]:
    return records[:]

# Returns a dict of the stems and their associated filters
def stem_list() -> dict[str, Callable[[list[dict[str, str]]],
                                      list[dict[str, str]]]]:
    return {'users': filter_users, 'Courses' : filter_courses,
            'Enrollments': filter_enrollments }

# Reads a CSV file into a list of dictionaries, one dictionary per
# row of data in the CSV file.  For each row, the keys of the dict are
# the CSV column titles, and the values are the corresponding data
# values from the row.
def read_from_csv(infile:Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    with open(infile, newline='') as f:
        reader = csv.DictReader(f) # Turns each row into a dictionary
        for row in reader:
            # Remove BOM from key, if present
            # See https://en.wikipedia.org/wiki/Byte_order_mark for detail
            newrow = row.copy()
            for key in row.keys():
                newkey:str = key
                
                # UTF-8 3-character BOM (0xEFBBBF)
                if key.startswith(chr(239) + chr(187) + chr(191)):
                    newkey = key[3:]
                # UTF-16 1-character BOM (0xFEFF or 0xFFFE)
                elif key.startswith('\ufeff') or key.startswith('\ufffe'):
                    newkey = key[1:]

                # Strip out the BOM if present    
                if newkey != key:
                    newrow[newkey] = row[key]
                    del newrow[key]
                    
            records.append(newrow)
    # Post: for all 0 <= i < j < len(records),
    #              records[i].keys() == records[j].keys()
    # The dictReader guarantees this is true, BTW.
    return records

# Takes a list of records--each a dictionary--and writes them to a CSV
# file.
def write_outfile(records: list[dict[str, str]], outfile:Path) -> None:
    # Pre: for all 0 <= i < j < len(records),
    #              records[i].keys() == records[j].keys()
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        for row in records:
            writer.writerow(row)

# Takes a STEM, a pair of directories DATA_DIRS, and a filter function
# STEM_FILTER.  Reads an input CSV file, filters the resulting records
# using STEM_FILTER, and writes the result to an output CSV file.
def filter_csv(stem:str, data_dirs:dict[str, Path],
           stem_filter:Callable[[list[dict[str, str]]], \
                                list[dict[str, str]]]) -> None:
    infile:Path = data_dirs['inputdir'].joinpath(stem + '.csv')
    inrecords: list[dict[str, str]] = read_from_csv(infile)
    #print(inrecords[:30])
    outrecords: list[dict[str, str]] = stem_filter(inrecords)
    outfile:Path = data_dirs['outputdir'].joinpath(stem + '.csv')
    write_outfile(outrecords, outfile)
