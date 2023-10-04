import sys
import io
import datetime
from mock import patch
import pytest
from fulgurate import Card, files
from fulgurate._cmd_line.show_schedule import main
from ._mock_ttyio import mock_ttyio
from ._shared import FixNowDatetime

_time_fmt = "%Y-%m-%d"
_cards_time = datetime.datetime(2022, 10, 18)

@pytest.fixture(scope='function')
def test_cards_path(tmpdir):
    cards_path = str(tmpdir / "cards")
    deck = [
        Card("a", "b", _cards_time),
        Card("c", "d", _cards_time),
        Card("e", "f", _cards_time),
    ]
    deck[0].repeat(5, _cards_time)
    with open(cards_path, 'w') as out_file:
        files.save(out_file, deck)
    return cards_path

def test_set_time_shortly_after(test_cards_path):
    set_time = _cards_time + datetime.timedelta(hours=2)
    set_time_str = set_time.strftime(_time_fmt)
    card_time_day_later_str = (_cards_time + datetime.timedelta(days=1)).strftime(_time_fmt)
    with open(test_cards_path) as in_file:
        num_cards = len(list(files.load(in_file)))

    with patch.object(sys, 'stdout', io.BytesIO()) as output, \
         patch.object(sys, 'argv', ["", "-n", set_time_str, str(test_cards_path)]):
        main()

    assert output.getvalue().splitlines() == [
        "%s %i %i" % (set_time_str, -1, num_cards - 1),
        "%s %i %i" % (card_time_day_later_str, 1, 1),
    ]

def test_no_set_time_layer(test_cards_path):
    now_time = _cards_time + datetime.timedelta(days=3)
    now_time_str = now_time.strftime(_time_fmt)
    card_time_day_later_str = (_cards_time + datetime.timedelta(days=1)).strftime(_time_fmt)
    with open(test_cards_path) as in_file:
        num_cards = len(list(files.load(in_file)))

    with patch.object(datetime, 'datetime', FixNowDatetime(now_time)), \
         patch.object(sys, 'stdout', io.BytesIO()) as output, \
         patch.object(sys, 'argv', ["", str(test_cards_path)]):
        main()

    assert output.getvalue().splitlines() == [
        "%s %i %i" % (now_time_str, -1, num_cards - 1),
        "%s %i %i" % (card_time_day_later_str, -2, 1),
    ]
