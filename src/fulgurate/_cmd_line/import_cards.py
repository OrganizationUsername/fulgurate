#!/usr/bin/env python2

"""
Takes a tab-separated value file where the columns correspond to the first
(top) and second (bottom) fields of the card respectively, and produces a cards
file with the cards at initial state.
"""

import sys
import argparse
from .._card import Card
from .. import files
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
    _args.add_now(arg_parser)
    return arg_parser

def main():
    """
    Entry point.
    """
    args = make_arg_parser().parse_args()

    _import(args.input_file, args.output_file, args.now)

if __name__ == "__main__":
    main()
