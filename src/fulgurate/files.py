"""
Cards file IO.
"""

import datetime
from contextlib2 import ExitStack
from ._card import Card
from . import _argopen

__all__ = (
    'TIME_FMT',
    'save',
    'load',
    'save_all',
    'load_all',
)

TIME_FMT = "%Y-%m-%d"

def save(cards, out_file):
    """
    Save cards to a file.
    """
    for card in cards:
        print >> out_file, '\t'.join((
            card.time.strftime(TIME_FMT),
            str(card.repetitions),
            str(card.interval),
            str(card.easiness),
            card.top,
            card.bottom,
        ))

def load(in_file):
    """
    Load cards from a file.
    """
    for line in in_file:
        parts = line.strip().split('\t')
        if len(parts) != 6:
            raise IOError("wrong number of records on line")
        time, repetitions, interval, easiness, top, bottom = parts
        yield Card(
            top,
            bottom,
            time=datetime.datetime.strptime(time, TIME_FMT),
            repetitions=int(repetitions),
            interval=float(interval),
            easiness=float(easiness),
        )

def save_all(cards):
    """
    Given cards with the filename field set, save them to their respectively files.
    """
    outputs = {}
    with ExitStack() as file_stack:
        for card in cards:
            if card.filename not in outputs:
                out_file = _argopen.open(card.filename, 'w')
                outputs[card.filename] = file_stack.enter_context(out_file)
            save([card], outputs[card.filename])

def load_all(filenames):
    """
    Load cards from multiple files, with the filename field set.
    """
    for filename in filenames:
        with _argopen.open(filename) as in_file:
            for card in load(in_file):
                card.filename = filename
                yield card
