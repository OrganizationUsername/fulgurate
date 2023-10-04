#!/usr/bin/env python2

"""
Prints information about how the cards in a file are currently scheduled. The
first column in the output is the date, the second is number of days in the
future, and the third is the number of cards scheduled for that time. A -1 in
the second column indicates new cards, while 0 indicates the cards that are
ready for review.
"""

import collections
import argparse
from .. import files, _argopen
from . import _args

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

def make_arg_parser():
    arg_parser = argparse.ArgumentParser(description=__doc__.strip())
    arg_parser.add_argument(
        'input_path',
        metavar="DECK-FILE",
        type=str,
        default="-",
        nargs="?",
        help="Path to input deck file.",
    )
    _args.add_now(arg_parser)
    return arg_parser

def main():
    """
    Entry point.
    """
    args = make_arg_parser().parse_args()

    with _argopen.open(args.input_path) as in_file:
        deck = tuple(files.load(in_file))

    args.now = args.now.replace(hour=0, minute=0, second=0, microsecond=0)

    _show_schedule(deck, args.now)

if __name__ == "__main__":
    main()
