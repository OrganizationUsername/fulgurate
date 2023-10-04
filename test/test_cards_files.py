import datetime
import pytest
from fulgurate import cards

_time = datetime.datetime(2022, 10, 18)

def _check_decks_equal(input_deck, output_deck):
    assert len(output_deck) == len(input_deck)
    for got_card, want_card in zip(output_deck, input_deck):
        assert got_card.top == want_card.top
        assert got_card.bot == want_card.bot
        assert got_card.time == want_card.time
        assert got_card.repetitions == want_card.repetitions
        assert got_card.interval == want_card.interval
        assert got_card.easiness == want_card.easiness
        assert got_card.is_new == want_card.is_new

def test_save_load(tmpdir):
    cards_path = str(tmpdir / "cards")

    input_deck = [
        cards.card("a", "b", _time, repetitions=0, interval=1.0, easiness=2.5),
        cards.card("c", "d", _time, repetitions=1, interval=1.0, easiness=2.36),
        cards.card("e", "f", _time, repetitions=2, interval=6.0, easiness=2.22),
    ]

    with open(cards_path, 'w') as out_file:
        cards.save(out_file, input_deck)
    with open(cards_path) as in_file:
        output_deck = tuple(cards.load(in_file))

    _check_decks_equal(input_deck, output_deck)

def test_load_error(tmpdir):
    tsv_path = str(tmpdir / "cards")

    with open(tsv_path, 'w') as out_file:
        print >> out_file, "\t".join(["a", "b", "c"])

    with open(tsv_path) as in_file:
        with pytest.raises(IOError):
            tuple(cards.load(in_file))

def test_save_all_load_all(tmpdir):
    cards_path0 = str(tmpdir / "cards0")
    cards_path1 = str(tmpdir / "cards1")

    input_deck = [
        cards.card("a", "b", _time, repetitions=0, interval=1.0, easiness=2.5),
        cards.card("c", "d", _time, repetitions=1, interval=1.0, easiness=2.36),
        cards.card("e", "f", _time, repetitions=2, interval=6.0, easiness=2.22),
    ]
    input_deck[0].filename = cards_path0
    input_deck[1].filename = cards_path1
    input_deck[2].filename = cards_path0

    cards.save_all(input_deck)
    output_deck = list(cards.load_all([cards_path0, cards_path1]))

    output_deck.sort(key=lambda c: c.top)
    _check_decks_equal(input_deck, output_deck)
