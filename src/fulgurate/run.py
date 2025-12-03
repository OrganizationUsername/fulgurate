"""
Management of practice cycle for cards.
"""

import random
import itertools

__all__ = (
    'CardFetcher',
    'run_cards',
    'bulk_review',
)

class CardFetcher:
    def __init__(self, cards, now, max_reviews=None, max_new=None, randomize=False):
        """
        Manages choosing cards to practice successively. This is a base for
        making practice systems.

        `now` is the current time for the review. Does up to `max_reviews`
        reviews and `max_new` cards before stopping. If `randomize` is set,
        then reviews happen in random order.
        """
        self._new_cards = list(itertools.islice((c for c in cards if c.is_new), max_new))
        self._new_cards.reverse()
        self._to_review = list(itertools.islice(
            (c for c in cards if not c.is_new and c.next_time <= now),
            max_reviews,
        ))
        self._to_review.reverse()
        if randomize:
            random.shuffle(self._to_review)

    def choose_next(self):
        """
        Get the next card to review, or `None` if there are none left to review.
        """
        if self._to_review:
            return self._to_review.pop()
        if self._new_cards:
            return self._new_cards.pop()
        return None

    def reject_card(self, card):
        """
        Reject card, putting it back for further practice in this run.
        """
        if card.is_new:
            self._new_cards.insert(0, card)
        else:
            self._to_review.insert(0, card)

def run_cards(cards, now, review_card, max_reviews=None, max_new=None, randomize=False):
    """
    Review cards one a time.

    `now` is the current time for the review. Does up to `max_reviews` reviews
    and `max_new` cards before stopping. If `randomize` is set, then reviews
    happen in random order.

    `review_card` is a callable which takes a card to review and returns the
    quality for the repetition. This function can manage any UI for the review.
    """

    fetcher = CardFetcher(cards, now, max_reviews, max_new, randomize)

    while (current := fetcher.choose_next()) is not None:
        quality = review_card(current)
        current.repeat(quality, now)
        if current.is_new:
            fetcher.reject_card(current)

def bulk_review(
    cards,
    now,
    batch_size,
    show_batch,
    review_card,
    max_reviews=None,
    max_new=None,
    randomize=False,
    randomize_batch=False,
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

    fetcher = CardFetcher(cards, now, max_reviews, max_new, randomize)

    def run_card(card):
        quality = review_card(card)
        card.repeat(quality, now)
        return quality

    batch = [c for _ in range(batch_size) for c in (fetcher.choose_next(),) if c is not None]
    while batch:
        if randomize_batch:
            random.shuffle(batch)

        show_batch(batch)
        for card in batch:
            run_card(card)
        batch = [c for c in batch if c.is_new]

        while len(batch) < batch_size:
            card = fetcher.choose_next()
            if card is None:
                break
            batch.append(card)
