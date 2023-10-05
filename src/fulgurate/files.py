"""
Cards file IO.
"""

import datetime
import csv
from contextlib2 import ExitStack
from ._card import Card

__all__ = (
    'write_cards',
    'read_cards',
    'save',
    'load',
    'save_all',
    'load_all',
)

_TIME_FMT = "%Y-%m-%d"
_CSV_DIALECT = csv.excel_tab # pylint: disable=invalid-name
_FIELD_NAMES = (
    'last repeat time',
    'repetitions',
    'interval',
    'easiness',
    'top',
    'bottom',
)

def _make_default_writer(out_file):
    return csv.DictWriter(out_file, fieldnames=_FIELD_NAMES, dialect=_CSV_DIALECT)

def _make_default_reader(in_file):
    return csv.DictReader(in_file, fieldnames=_FIELD_NAMES, dialect=_CSV_DIALECT)

def write_cards(cards, writer):
    """
    Write cards to a `csv.DictWriter`.
    """
    for card in cards:
        writer.writerow({
            'top': card.top,
            'bottom': card.bottom,
            'last repeat time': card.last_repeat_time.strftime(_TIME_FMT),
            'repetitions': card.repetitions,
            'interval': card.interval,
            'easiness': card.easiness,
        })

def read_cards(reader):
    """
    Read cards from a `csv.DictReader`.
    """
    for row in reader:
        yield Card(
            row['top'],
            row['bottom'],
            last_repeat_time=datetime.datetime.strptime(row['last repeat time'], _TIME_FMT),
            repetitions=int(row['repetitions']),
            interval=float(row['interval']),
            easiness=float(row['easiness']),
        )

def save(cards, out_file, make_writer=None):
    """
    Save cards to a file.
    """
    if make_writer is None:
        make_writer = _make_default_writer
    writer = make_writer(out_file)
    write_cards(cards, writer)

def load(in_file, make_reader=None):
    """
    Load cards from a file.
    """
    if make_reader is None:
        make_reader = _make_default_reader
    reader = make_reader(in_file)
    for card in read_cards(reader):
        yield card

def save_all(cards, make_writer=None):
    """
    Given cards with the filename field set, save them to their respectively files.
    """
    outputs = {}
    with ExitStack() as file_stack:
        for card in cards:
            if card.filename not in outputs:
                out_file = open(card.filename, 'w')
                outputs[card.filename] = file_stack.enter_context(out_file)
            save([card], outputs[card.filename], make_writer=make_writer)

def load_all(filenames, make_reader=None):
    """
    Load cards from multiple files, with the filename field set.
    """
    for filename in filenames:
        with open(filename) as in_file:
            for card in load(in_file, make_reader=make_reader):
                card.filename = filename
                yield card
