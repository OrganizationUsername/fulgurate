"""
Management of run cycle for cards.
"""

import random
import itertools

def fetch_cards(cards, now, max_reviews=None, max_new=None, randomize=False):
  new_cards = list(itertools.islice((c for c in cards if c.is_new), max_new))
  new_cards.reverse()
  to_review = list(itertools.islice((c for c in cards if not c.is_new and c.next_time <= now), max_reviews))
  to_review.reverse()
  if randomize:
    random.shuffle(to_review)
  def choose_next():
    if len(to_review) > 0:
      return to_review.pop()
    elif len(new_cards) > 0:
      return new_cards.pop()
    else:
      return None
  def reject_card(card):
    if card.is_new:
      new_cards.insert(0, card)
    else:
      to_review.insert(0, card)
  return choose_next, reject_card

def run_cards(cards, now, review_card, max_reviews=None, max_new=None, randomize=False):
  choose_next, reject_card = fetch_cards(cards, now, max_reviews, max_new, randomize)

  while True:
    current = choose_next()
    if current is None:
      break
    quality = review_card(current)
    current.repeat(quality, now)
    if current.is_new:
      reject_card(current)

def bulk_review(cards, now, batch_size, show_batch, review_card, max_reviews=None, max_new=None, randomize=False, randomize_batch=True):
  choose_next, reject_card = fetch_cards(cards, now, max_reviews, max_new, randomize)

  batch = [n for i in range(batch_size) for n in [choose_next()] if n is not None]
  while len(batch) > 0:
    if randomize_batch:
      random.shuffle(batch)

    show_batch(batch)
    def run_card(card):
      quality = review_card(card)
      card.repeat(quality, now)
      return quality
    batch = [c for c in batch for r in [run_card(c)] if c.is_new]
    
    while len(batch) < batch_size:
      next = choose_next()
      if next is None:
        break
      batch.append(next)
