#!/usr/bin/env python2

"""
Takes a tab-separated value file where the columns correspond to the first
(top) and second (bottom) fields of the card respectively, and produces a cards
file with the cards at initial state.
"""

import sys
import csv
import argparse
from .._card import Card
from .. import files
from . import _args

_INPUT_FIELD_NAMES = ('top', 'bottom')
_SNIFF_TSV_DIALECT = "sniff-tsv"
_SNIFF_CSV_DIALECT = "sniff-csv"
_DEFAULT_CSV_DIALECT = _SNIFF_TSV_DIALECT

def _sniff_csv_dialect(in_file, sep):
    csv_sample = in_file.read(1024)
    in_file.seek(0)
    return csv.Sniffer().sniff(csv_sample, sep)

def _load_data(in_file, dialect, read_header):
    if dialect == _SNIFF_TSV_DIALECT:
        dialect = _sniff_csv_dialect(in_file, "\t")
    elif dialect == _SNIFF_CSV_DIALECT:
        dialect = _sniff_csv_dialect(in_file, ",")

    field_names = None if read_header else _INPUT_FIELD_NAMES

    reader = csv.DictReader(in_file, fieldnames=field_names, dialect=dialect)
    if read_header:
        unknown_field_names = set(reader.fieldnames) - set(_INPUT_FIELD_NAMES)
        if unknown_field_names:
            raise ValueError("unknown field names in input: %s" % (",".join(unknown_field_names)))
    for row in reader:
        yield row

def _import(in_file, out_file, now, csv_dialect, read_csv_header):
    data = _load_data(in_file, dialect=csv_dialect, read_header=read_csv_header)
    cards = (Card(row['top'], row['bottom'], now) for row in data)
    files.save(cards, out_file)

def make_arg_parser():
    arg_parser = argparse.ArgumentParser(description=__doc__.strip())
    arg_parser.add_argument(
        'input_file',
        metavar="INPUT-FILE",
        type=argparse.FileType('r'),
        default=sys.stdin,
        nargs='?',
        help="Path to input cards file.",
    )
    arg_parser.add_argument(
        'output_file',
        metavar="DECK-FILE",
        type=argparse.FileType('w'),
        default=sys.stdout,
        nargs='?',
        help="Path to output deck file.",
    )
    arg_parser.add_argument(
        '-d',
        '--dialect',
        dest='csv_dialect',
        type=str,
        choices=[_SNIFF_TSV_DIALECT, _SNIFF_CSV_DIALECT] + csv.list_dialects(),
        default=_SNIFF_TSV_DIALECT,
        help="The CSV dialect from Python's csv module to use for reading input cards. If %s " \
             " then try to auto-detect a TSV dialect; if %s then try to auto-detect a CSV" \
             " dialect. Defaults to %s." \
             % (_SNIFF_TSV_DIALECT, _SNIFF_CSV_DIALECT, _DEFAULT_CSV_DIALECT)
    )
    arg_parser.add_argument(
        '-H',
        '--no-header',
        dest='read_csv_header',
        default=True,
        action='store_false',
        help="Disable reading of a the first input row as a header.",
    )
    _args.add_now(arg_parser)
    return arg_parser

def main():
    """
    Entry point.
    """
    args = make_arg_parser().parse_args()

    _import(
        args.input_file,
        args.output_file,
        now=args.now,
        csv_dialect=args.csv_dialect,
        read_csv_header=args.read_csv_header,
    )

if __name__ == "__main__":
    main()
