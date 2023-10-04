#!/usr/bin/env python2

"""
NAME
----

fulgurate-import - convert a two-column TSV file to a flashcard file

SYNOPSIS
--------

*fulgurate-import* ['OPTIONS'] TSV-FILE [CARDS-FILE]

DESCRIPTION
-----------

Takes a tab-separated value file where the columns correspond to the first
(top) and second (bottom) fields of the card respectively, and produces a cards
file with the cards at initial state.

OPTIONS
-------

*-n* 'YYYY-MM-DD'::
  Set the current time. Defaults to the system clock.
"""

import sys
import datetime
import getopt
from .._card import Card
from .. import files, _argopen

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

def main():
    """
    Entry point.
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:")
        if len(args) < 1 or len(args) > 2:
            raise getopt.GetoptError("wrong number of positional arguments")
    except getopt.GetoptError:
        print >> sys.stderr, "usage: %s [-n TIME] DATA-FILE [CARDS-FILE]" % (sys.argv[0])
        sys.exit(1)

    now = datetime.datetime.now()
    for opt, arg in opts:
        if opt == '-n':
            import dateutil.parser
            now = dateutil.parser.parse(arg)

    src = args[0]
    dest = args[1] if len(args) > 1 else "-"
    with _argopen.open(src) as in_file, \
         _argopen.open(dest, 'w') as out_file:
        _import(in_file, out_file, now)

if __name__ == "__main__":
    main()
