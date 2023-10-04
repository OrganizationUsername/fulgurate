import sys
import io
import collections
import datetime
from mock import patch, Mock, ANY
import pytest
from fulgurate import cards
from fulgurate.cmd_line import _run
from fulgurate.cmd_line._run import main, external_filter, review_card
from ._mock_ttyio import mock_ttyio
from ._shared import FixNowDatetime

_time_fmt = "%Y-%m-%d"
_cards_time = datetime.datetime(2022, 10, 18)

@pytest.fixture(scope='function')
def test_cards_path(tmpdir):
    cards_path = str(tmpdir / "cards")
    deck = [
        cards.card("a", "b", _cards_time),
        cards.card("c", "d", _cards_time),
        cards.card("e", "f", _cards_time),
    ]
    with open(cards_path, 'w') as out_file:
        cards.save(out_file, deck)
    return cards_path

def _minimal_call(args, key_inputs=[]):
    """Call that mocks out the whole of the run."""
    with patch.object(cards, 'run_cards') as run_cards_mock, \
         mock_ttyio(key_inputs), \
         patch.object(sys, 'argv', [""] + list(args)):
        main()
    return run_cards_mock

def _minimal_real_call(args, key_inputs=[]):
    """Call that does a real run but mocks interaction."""
    with patch.object(_run, 'review_card', Mock(return_value=5)) as review_card_mock, \
         patch.object(_run, 'external_filter') as external_filter_mock, \
         mock_ttyio(key_inputs), \
         patch.object(sys, 'argv', [""] + list(args)):
        main()
    return review_card_mock, external_filter_mock

def _assert_run_cards_called_once_with(mock, cards=ANY, now=ANY, review_card=ANY, max_reviews=ANY,
                                       max_new=ANY, randomize=ANY):
    mock.assert_called_once_with(cards, now, review_card, max_reviews=max_reviews, max_new=max_new,
                                 randomize=randomize)

def _assert_bulk_review_called_once_with(mock, cards=ANY, now=ANY, batch_size=ANY, show_batch=ANY,
                                         review_card=ANY, max_reviews=ANY, max_new=ANY,
                                         randomize=ANY):
    mock.assert_called_once_with(cards, now, batch_size, show_batch, review_card,
                                 max_reviews=max_reviews, max_new=max_new, randomize=randomize)

def _assert_review_card_called_with(mock, card=ANY, ext_filter=ANY, ext_finish=ANY):
    mock.assert_called_with(card, ext_filter=ext_filter, ext_finish=ext_finish)

@pytest.mark.xfail(reason="command line is bugged")
def test_run_basic(test_cards_path):
    set_time = _cards_time
    set_time_str = set_time.strftime(_time_fmt)
    with open(test_cards_path) as in_file:
        deck = list(cards.load(in_file))

    key_inputs = ["x", "`"] * len(deck) + ["x", "1"] * len(deck) \
        + ["x", "2"] * len(deck) + ["y", "3", "y", "4", "y", "5"]
    output = io.BytesIO()
    with mock_ttyio(key_inputs, "CLEAR"), \
         patch.object(sys, 'stdout', io.BytesIO()) as output, \
         patch.object(sys, 'argv', ["", "-n", set_time_str, str(test_cards_path)]):
        main()

    output = zip(*([iter(output.getvalue().splitlines())] * 4))
    assert len(output) == len(deck) * 4
    for (got_clear_line, got_cards_line, got_top, got_bot), want_card in zip(output, deck):
        assert got_clear_line == "CLEAR"
        assert got_cards_line == test_cards_path
        assert got_top == want_card.top
        assert got_bot == want_card.bot
    with open(test_cards_path) as in_file:
        new_deck = tuple(cards.load(in_file))
        assert new_deck[0].easiness <= new_deck[1].easiness < new_deck[2].easiness \
            < min(c.easiness for c in deck)

def test_run_no_set_time(test_cards_path):
    now_time = _cards_time + datetime.timedelta(days=3)
    with patch.object(datetime, 'datetime', FixNowDatetime(now_time)):
        run_cards_mock = _minimal_call([str(test_cards_path)])
    _assert_run_cards_called_once_with(run_cards_mock, now=now_time)

def test_run_set_time(test_cards_path):
    set_time = _cards_time + datetime.timedelta(days=2)
    run_cards_mock = _minimal_call(["-n", set_time.strftime(_time_fmt), str(test_cards_path)])
    _assert_run_cards_called_once_with(run_cards_mock, now=set_time)

def test_run_set_max_reviews(test_cards_path):
    set_time = _cards_time + datetime.timedelta(days=2)
    run_cards_mock = _minimal_call(["-R", 12, str(test_cards_path)])
    _assert_run_cards_called_once_with(run_cards_mock, max_reviews=12)

def test_run_set_max_new(test_cards_path):
    set_time = _cards_time + datetime.timedelta(days=2)
    run_cards_mock = _minimal_call(["-N", 34, str(test_cards_path)])
    _assert_run_cards_called_once_with(run_cards_mock, max_new=34)

def test_run_set_randomize(test_cards_path):
    set_time = _cards_time + datetime.timedelta(days=2)
    run_cards_mock = _minimal_call(["-r", str(test_cards_path)])
    _assert_run_cards_called_once_with(run_cards_mock, randomize=True)

def test_run_set_batch_size(test_cards_path):
    set_time = _cards_time + datetime.timedelta(days=2)
    with patch.object(cards, 'bulk_review') as bulk_review_mock:
        _minimal_call(["-b", 56, str(test_cards_path)])
    _assert_bulk_review_called_once_with(bulk_review_mock, batch_size=56)

def test_external_filter():
    card0 = cards.card("abc", "def", _cards_time)
    card0.filename = "file0"
    card1 = cards.card("efg", "hij", _cards_time)
    card1.filename = "file1"

    f = external_filter("rev")
    f.send_card(card0)
    f.send_card(card1)
    f.close()
    assert f.receive() == ("fed", "cba", "0elif")
    assert f.receive() == ("jih", "gfe", "1elif")

def test_run_ext_filter(test_cards_path):
    review_card_mock, ext_filter_mock = _minimal_real_call(["-f", "abc", str(test_cards_path)])
    ext_filter_mock.assert_called_once_with("abc")
    _assert_review_card_called_with(review_card_mock, ext_filter=ext_filter_mock.return_value)

def test_run_ext_finish(test_cards_path):
    review_card_mock, ext_filter_mock = _minimal_real_call(["-F", "def", str(test_cards_path)])
    ext_filter_mock.assert_called_once_with("def")
    _assert_review_card_called_with(review_card_mock, ext_finish=ext_filter_mock.return_value)
