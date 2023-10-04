import sys
import os.path
import datetime
import pytest
from mock import patch
from fulgurate import cards
from fulgurate.cmd_line._import import main
from ._mock_ttyio import mock_ttyio
from ._shared import FixNowDatetime

_time_fmt = "%Y-%m-%d"
_example_path = os.path.join(os.path.dirname(__file__), "..", "..", "example.tsv")

def _load_raw_cards(in_file):
    for line in in_file:
        if line.startswith("#"):
            continue
        parts = line.strip().split('\t')
        assert len(parts) == 2
        yield(parts)

def _minimal_call(args):
    with patch.object(cards, 'save') as save_mock, \
         patch.object(sys, 'argv', [""] + list(args)):
        main()
    return save_mock

def test_basic(tmpdir):
    cards_path = str(tmpdir / "cards")
    with open(_example_path) as in_file:
        input_data = tuple(_load_raw_cards(in_file))

    with patch.object(sys, 'argv', ["", _example_path, cards_path]):
        main()

    with open(cards_path) as in_file:
        deck = tuple(cards.load(in_file))
    assert len(deck) == len(input_data)
    assert all(c.top == t and c.bot == b for c, (t, b) in zip(deck, input_data))
    assert all(c.is_new for c in deck)
    assert all(c.repetitions == 0 for c in deck)

def test_no_set_time(tmpdir):
    now_time = datetime.datetime(2021, 12, 24)
    cards_path = str(tmpdir / "cards")
    with patch.object(datetime, 'datetime', FixNowDatetime(now_time)):
        save_mock = _minimal_call([str(_example_path), str(cards_path)])
    assert all(c.time == now_time for c in save_mock.call_args[1])

@pytest.mark.xfail(reason="command line is bugged")
def test_set_time(tmpdir):
    cards_path = str(tmpdir / "cards")
    set_time = datetime.datetime(2022, 10, 18)
    save_mock = _minimal_call([
        "-n", set_time.strftime(_time_fmt),
        str(_example_path),
        str(cards_path),
    ])
    assert all(c.time == set_time for c in save_mock.call_args[1])
