"""
Cards file IO.
"""

import datetime
from ._card import Card

time_fmt = "%Y-%m-%d"

def save(output, cards):
  for card in cards:
    parts = (card.time.strftime(time_fmt), str(card.repetitions), str(card.interval), str(card.easiness), card.top, card.bot)
    print >> output, '\t'.join(parts)

def load(input):
  for line in input:
    parts = line.strip().split('\t')
    if len(parts) != 6:
      raise IOError("wrong number of records on line")
    time, repetitions, interval, easiness, top, bot = parts
    time = datetime.datetime.strptime(time, time_fmt)
    repetitions = int(repetitions)
    interval = float(interval)
    easiness = float(easiness)
    new = Card(top, bot, time, repetitions, interval, easiness)
    yield new

def save_all(cards):
  import argopen
  outputs = {}
  try:
    for card in cards:
      if card.filename not in outputs:
        outputs[card.filename] = argopen.open(card.filename, 'w')
      save(outputs[card.filename], [card])
  finally:
    for output in outputs.values():
      output.close()

def load_all(filenames):
  import argopen
  for filename in filenames:
    with argopen.open(filename) as input:
      for card in load(input):
        card.filename = filename
        yield card
