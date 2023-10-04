#!/usr/bin/env python2

"""
Takes a tab-separated value file where the columns correspond to the first
(top) and second (bottom) fields of the card respectively, and produces a cards
file with the cards at initial state.
"""

import argparse
from .._card import Card
from .. import files, _argopen
from . import _args

def _load_data(in_file):
    for i, line in enumerate(in_file, 1):
        if line.startswith('#'):
            continue
        parts = line.strip().split('\t')
        if len(parts) != 2:
            raise IOError("wrong number of records on line %i" % (i))
        yield parts

def _import(in_file, out_file, now):
    files.save(
        (
            Card(top, bottom, now)
            for top, bottom in _load_data(in_file)
        ),
        out_file,
    )

def make_arg_parser():
    arg_parser = argparse.ArgumentParser(description=__doc__.strip())
    arg_parser.add_argument(
        'input_path',
        metavar="INPUT-FILE",
        type=str,
        default="-",
        nargs='?',
        help="Path to input cards file.",
    )
    arg_parser.add_argument(
        'output_path',
        metavar="DECK-FILE",
        type=str,
        default="-",
        nargs='?',
        help="Path to output deck file.",
    )
    _args.add_now(arg_parser)
    return arg_parser

def main():
    """
    Entry point.
    """
    args = make_arg_parser().parse_args()

    with _argopen.open(args.input_path) as in_file, \
         _argopen.open(args.output_path, 'w') as out_file:
        _import(in_file, out_file, args.now)

if __name__ == "__main__":
    main()
