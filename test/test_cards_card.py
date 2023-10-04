import datetime
import pytest
from fulgurate import cards

_time = datetime.datetime(2022, 10, 18)
_eps = 0.001

def _make_repetitions_cases(repetitions, interval, easiness):
    for i in range(0, 6):
        card = cards.card("a", "b", _time, repetitions=repetitions, interval=interval,
                          easiness=easiness)
        card.repeat(i, _time)
        yield card.repetitions, card.interval, card.easiness

def _compare_repetitions_cases(got, want):
    got = list(got)
    if len(got) != len(want):
        return False
    return all(
        r0 == r1 and abs(i0 - i1) < _eps and abs(e0 - e1) < _eps
        for (r0, i0, e0), (r1, i1, e1) in zip(got, want)
    )

def test_new_card():
    card = cards.card("a", "b", _time, repetitions=0, interval=1, easiness=2.5)
    assert card.top == "a"
    assert card.bot == "b"
    assert card.time == _time
    assert card.repetitions == 0
    assert card.interval == 1
    assert card.easiness == 2.5
    assert card.is_new

    card = cards.card("a", "b", _time, repetitions=1, interval=2.34, easiness=5.67)
    assert card.top == "a"
    assert card.bot == "b"
    assert card.time == _time
    assert card.repetitions == 1
    assert card.interval == 2.34
    assert card.easiness == 5.67
    assert not card.is_new

def test_repeat():
    assert _compare_repetitions_cases(_make_repetitions_cases(0, 1.0, 2.5), [
        (0, 1.0, 1.7), (0, 1.0, 1.96), (0, 1.0, 2.18),
        (1, 1.0, 2.36), (1, 1.0, 2.5), (1, 1.0, 2.6),
    ])
    assert _compare_repetitions_cases(_make_repetitions_cases(1, 1.0, 2.36), [
        (0, 1.0, 1.56), (0, 1.0, 1.82), (0, 1.0, 2.04),
        (2, 6.0, 2.22), (2, 6.0, 2.36), (2, 6.0, 2.46),
    ])
    assert _compare_repetitions_cases(_make_repetitions_cases(2, 6.0, 2.22), [
        (0, 6.0, 1.42), (0, 6.0, 1.68), (0, 6.0, 1.90),
        (3, 12.48, 2.08), (3, 13.32, 2.22), (3, 13.92, 2.32),
    ])
    assert _compare_repetitions_cases(_make_repetitions_cases(3, 12.48, 2.08), [
        (0, 12.48, 1.3), (0, 12.48, 1.54), (0, 12.48, 1.76),
        (4, 24.2112, 1.94), (4, 25.9584, 2.08), (4, 27.2064, 2.18),
    ])

def test_github_issue_1_wrong_interval_update():
    def compare(got, want):
        # Only look at interval
        got = [(0, i, 0) for _, i, _ in got]
        want = [(0, i, 0) for i in want]
        return _compare_repetitions_cases(got, want)
    # Interval shouldn't change for repetitions of 0
    assert compare(_make_repetitions_cases(0, 12.48, 2.08), [12.48, 12.48, 12.48, 1, 1, 1])
    assert compare(_make_repetitions_cases(1, 12.48, 2.08), [12.48, 12.48, 12.48, 6, 6, 6])

def test_next_time():
    assert cards.card("a", "b", _time, repetitions=0, interval=1.0, easiness=2.5) \
        .next_time == datetime.datetime(year=2022, month=10, day=19)
    assert cards.card("c", "d", _time, repetitions=1, interval=1.0, easiness=2.36) \
        .next_time == datetime.datetime(year=2022, month=10, day=19)
    assert cards.card("e", "f", _time, repetitions=2, interval=6.0, easiness=2.22) \
        .next_time == datetime.datetime(year=2022, month=10, day=24)
    assert cards.card("e", "f", _time, repetitions=3, interval=12.48, easiness=2.08) \
        .next_time == datetime.datetime(year=2022, month=10, day=31)

    assert cards.card("e", "f", _time, repetitions=0, interval=12.48, easiness=0.0) \
        .next_time == datetime.datetime(year=2022, month=10, day=31)
    assert cards.card("e", "f", _time, repetitions=10.0, interval=12.48, easiness=3.0) \
        .next_time == datetime.datetime(year=2022, month=10, day=31)
