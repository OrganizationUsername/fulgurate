"""
Management of run cycle for cards.
"""

import random
import itertools

__all__ = (
    'fetch_cards',
    'run_cards',
    'bulk_review',
)

def fetch_cards(cards, now, max_reviews=None, max_new=None, randomize=False):
    """
    Choose cards to review successively. This is a base for making review
    systems.

    `now` is the current time for the review. Does up to `max_reviews` reviews
    and `max_new` cards before stopping. If `randomize` is set, then reviews
    happen in random order.

    Returns `choose_next()` and `reject_card()`. Call the former to get the
    next card to review or `None` if there are no more, and the later to reject
    a card and put it back for review.
    """

    new_cards = list(itertools.islice((c for c in cards if c.is_new), max_new))
    new_cards.reverse()
    to_review = list(itertools.islice(
        (c for c in cards if not c.is_new and c.next_time <= now),
        max_reviews,
    ))
    to_review.reverse()
    if randomize:
        random.shuffle(to_review)

    def choose_next():
        if to_review:
            return to_review.pop()
        if new_cards:
            return new_cards.pop()
        return None

    def reject_card(card):
        if card.is_new:
            new_cards.insert(0, card)
        else:
            to_review.insert(0, card)

    return choose_next, reject_card

def run_cards(cards, now, review_card, max_reviews=None, max_new=None, randomize=False):
    """
    Review cards one a time.

    `now` is the current time for the review. Does up to `max_reviews` reviews
    and `max_new` cards before stopping. If `randomize` is set, then reviews
    happen in random order.

    `review_card` is a callable which takes a card to review and returns the
    quality for the repetition. This function can manage any UI for the review.
    """

    choose_next, reject_card = fetch_cards(cards, now, max_reviews, max_new, randomize)

    while True:
        current = choose_next()
        if current is None:
            break
        quality = review_card(current)
        current.repeat(quality, now)
        if current.is_new:
            reject_card(current)

def bulk_review(
    cards,
    now,
    batch_size,
    show_batch,
    review_card,
    max_reviews=None,
    max_new=None,
    randomize=False,
    randomize_batch=True,
):
    """
    Review cards in batches.

    `now` is the current time for the review. Does up to `max_reviews` reviews
    and `max_new` cards before stopping. If `randomize` is set, then reviews
    happen in random order. If `randomize_batch` is set, the order of each
    batch is also randomized.

    `batch_size` is the number of cards to show at once.

    `show_batch` is a callable which takes an iterable of cards in the batch.
    `review_card` is a callable which takes a card to review and returns the
    quality for the repetition. These functions can manage any UI for the
    review.
    """

    choose_next, _ = fetch_cards(cards, now, max_reviews, max_new, randomize)

    def run_card(card):
        quality = review_card(card)
        card.repeat(quality, now)
        return quality

    batch = [c for _ in range(batch_size) for c in (choose_next(),) if c is not None]
    while batch:
        if randomize_batch:
            random.shuffle(batch)

        show_batch(batch)
        for card in batch:
            run_card(card)
        batch = [c for c in batch if c.is_new]

        while len(batch) < batch_size:
            card = choose_next()
            if card is None:
                break
            batch.append(card)
