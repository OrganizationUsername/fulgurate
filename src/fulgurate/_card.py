"""
Flashcard data and core operations.
"""

import datetime
import math

class Card:
  def __init__(self, top, bot, time, repetitions=0, interval=1, easiness=2.5):
    self.top = top
    self.bot = bot
    self.time = time.replace(second=0, microsecond=0)
    self.repetitions = repetitions
    self.interval = interval
    self.easiness = easiness
    self.filename = None # Reserved for use by {load,save}_all

  def is_new(self):
    return self.repetitions == 0

  def next_time(self):
    return self.time + datetime.timedelta(days=math.ceil(self.interval))

  def repeat(self, quality, time):
    # SM-2
    assert quality >= 0 and quality <= 5
    self.easiness = max(1.3, self.easiness + 0.1 - (5.0 - quality) * (0.08 + (5.0 - quality) * 0.02))
    if quality < 3: self.repetitions = 0
    else: self.repetitions += 1
    if self.repetitions == 1: self.interval = 1
    elif self.repetitions == 2: self.interval = 6
    elif self.repetitions > 2: self.interval *= self.easiness
    self.time = time

  is_new = property(is_new)
  next_time = property(next_time)
