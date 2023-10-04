#!/usr/bin/env python2

"""
NAME
----

fulgurate-show-schedule - print information about card scheduling

SYNOPSIS
--------

*fulgurate-show-schedule* ['OPTIONS'] CARDS-FILE

DESCRIPTION
-----------

Prints information about how the cards in a file are currently scheduled. The
first column in the output is the date, the second is number of days in the
future, and the third is the number of cards scheduled for that time. A -1 in
the second column indicates new cards, while 0 indicates the cards that are
ready for review.

OPTIONS
-------

*-n* 'YYYY-MM-DD'::
  Set the current time. Defaults to the system clock.
"""

import sys
import datetime
import collections
import getopt
from .. import files, _argopen

def _show_schedule(deck, now):
    unseen = 0
    on_day = collections.defaultdict(int)
    for card in deck:
        if card.is_new:
            unseen += 1
        else:
            on_day[card.next_time] += 1

    print "%s %i %i" % (now.strftime(files.TIME_FMT), -1, unseen)
    schedule = [
        (next_time.strftime(files.TIME_FMT), (next_time - now).days, on_day[next_time])
        for next_time in on_day
    ]
    schedule.sort(key=lambda (t, d, n): d)
    for item in schedule:
        print "%s %i %i" % item

def main():
    """
    Entry point.
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:")
        if len(args) != 1:
            raise getopt.GetoptError("wrong number of positional arguments")
    except getopt.GetoptError:
        print >> sys.stderr, "usage: %s [-n TIME]" % (sys.argv[0])
        sys.exit(1)

    filename = args[0]
    with _argopen.open(filename) as in_file:
        deck = tuple(files.load(in_file))

    now = datetime.datetime.now()
    for opt, arg in opts:
        if opt == '-n':
            import dateutil.parser
            now = dateutil.parser.parse(arg)
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)

    _show_schedule(deck, now)

if __name__ == "__main__":
    main()
