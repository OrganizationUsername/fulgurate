#!/usr/bin/env python2

"""
NAME
----

fulgurate-run - run flashcards in the terminal

SYNOPSIS
--------

*fulgurate-run* ['OPTIONS'] CARDS-FILE [CARDS-FILE ...]

DESCRIPTION
-----------

Runs one or more sets of flashcards interactively at the terminal. Cards can be
presented individually (the default) or in batches where several cards will be
presented before user feedback is required.

The interaction for each card is as follows. The program first shows the first
(top) part of the card. Press any key after deciding on an answer. The program
then shows the second (bottom) part of the card. Press ~,1,2,3,4,5 for 0
through 5 respectively, indicating your evaluation of how well you remembered
the answer. 0 through 2 are failure responses and 3 through 5 are success.

OPTIONS
-------

*-n* 'YYYY-MM-DD'::
  Set the current time. Defaults to the system clock.

*-R* 'NUM'
  Set the maximum number of cards to review.

*-N* 'NUM'
  Set the maximum number of new cards.

*-r*
  Randomly order cards to review, from among all input card sets.

*-b* 'NUM'
  Enable batch mode and set the number of cards in one batch.

*-f* 'CMD'
  Set a command to filter cards. It should take on stdin a sequence of card
  data lines consisting of filename, first field, and second field, separated
  by tabs. It should output to stdout new card data in the same format, which
  will be shown instead of the original card data.

*-F* 'CMD'
  Set a command to execute after a card's second field is shown. It should take
  cards on stdin in the same format as the command for -f. Its output is
  ignored.
"""

import sys
import os
import subprocess
import datetime
import getopt
from .. import files, run
from . import _ttyio

def _show_batch(cards):
    _ttyio.clear()
    for i, card in enumerate(cards):
        print "%i: %s\r" % (i + 1, card.top)
    print "\r"

class _ExternalFilter(object):
    """
    Manages an external filter program.
    """
    def __init__(self, command):
        self.proc = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def send_card(self, card):
        """
        Send a card to the external filter program.
        """
        print >> self.proc.stdin, "%s\t%s\t%s" % (card.filename or "", card.top, card.bottom)
        self.proc.stdin.flush()

    def receive(self):
        """
        Get result from the external filter.
        """
        return tuple(
            p.decode('string_escape')
            for p in self.proc.stdout.readline().rstrip('\n').split('\t')
        )

    def close(self):
        """
        Close the program.
        """
        self.proc.stdin.close()
        os.waitpid(self.proc.pid, 0)

def _review_card(card, clear=True, wait=True, ext_filter=None, ext_finish=None):
    if clear:
        _ttyio.clear()
    with _ttyio.Unbuffered(sys.stdin):
        if ext_filter is None:
            filename, top, bottom = card.filename, card.top, card.bottom
        else:
            ext_filter.send_card(card)
            filename, top, bottom = ext_filter.receive()
        if filename:
            print "%s\r" % (filename)
        print "%s\r" % (top)
        if wait:
            _ttyio.getch()
        print "%s\r" % (bottom)
        if ext_finish is not None:
            ext_finish.send_card(card)
        while True:
            in_char = _ttyio.getch()
            if in_char == '`':
                return 0
            elif in_char in "12345":
                return int(in_char)

def _review_deck(deck, now, max_reviews, max_new, randomize, batch_size, ext_filter, ext_finish):
    # pylint: disable=no-value-for-parameter
    try:
        with _ttyio.Unbuffered(sys.stdin):
            now = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if batch_size is None:
                run.run_cards(
                    deck,
                    now,
                    lambda *args: _review_card(
                        *args,
                        ext_filter=ext_filter,
                        ext_finish=ext_finish
                    ),
                    max_reviews=max_reviews,
                    max_new=max_new,
                    randomize=randomize,
                )
            else:
                run.bulk_review(
                    deck,
                    now,
                    batch_size,
                    _show_batch,
                    lambda *args: _review_card(
                        *args,
                        clear=False,
                        wait=False,
                        ext_filter=ext_filter,
                        ext_finish=ext_finish
                    ),
                    max_reviews=max_reviews,
                    max_new=max_new,
                    randomize=randomize,
                )
    except KeyboardInterrupt:
        pass
    finally:
        files.save_all(deck)

def main():
    """
    Entry point.
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:R:N:rb:f:F:")
        if len(args) < 1:
            raise getopt.GetoptError("wrong number of positional arguments")
    except getopt.GetoptError:
        print >> sys.stderr, "usage: %s [-n TIME] [-R NUM] [-N NUM] [-r] [-b NUM] [-f CMD]" \
                             " [-F CMD] CARDS-FILE [...]" % (sys.argv[0])
        sys.exit(1)

    deck = tuple(files.load_all(args))

    now = datetime.datetime.now()
    max_reviews = None
    max_new = None
    randomize = False
    batch_size = None
    ext_filter = None
    ext_finish = None
    for opt, arg in opts:
        if opt == '-n':
            import dateutil.parser
            now = dateutil.parser.parse(arg)
        elif opt == '-R':
            max_reviews = int(arg)
        elif opt == '-N':
            max_new = int(arg)
        elif opt == '-r':
            randomize = True
        elif opt == '-b':
            batch_size = int(arg)
        elif opt == '-f':
            ext_filter = _ExternalFilter(arg)
        elif opt == '-F':
            ext_finish = _ExternalFilter(arg)

    _review_deck(
        deck=deck,
        now=now,
        max_reviews=max_reviews,
        max_new=max_new,
        randomize=randomize,
        batch_size=batch_size,
        ext_filter=ext_filter,
        ext_finish=ext_finish,
    )

if __name__ == "__main__":
    main()
