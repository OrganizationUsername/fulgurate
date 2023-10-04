"""
Flashcard data and core operations.
"""

import datetime
import math

class Card(object):
    """
    Flash card.
    """

    def __init__(self, top, bottom, time, repetitions=0, interval=1, easiness=2.5):
        self.top = top
        self.bottom = bottom
        self.time = time.replace(second=0, microsecond=0)
        self.repetitions = repetitions
        self.interval = interval
        self.easiness = easiness
        self.filename = None # Reserved for use by {load,save}_all

    @property
    def is_new(self):
        """
        Is this a new card (ie has no repetitions).
        """
        return self.repetitions == 0

    @property
    def next_time(self):
        """
        The time this card is currently scheduled for.
        """
        return self.time + datetime.timedelta(days=math.ceil(self.interval))

    def repeat(self, quality, time):
        """
        Do a repeatition of this card using SM-2.
        """
        if not (quality >= 0 and quality <= 5):
            raise ValueError("quality must be in 0-5")
        self.easiness = max(
            1.3,
            self.easiness + 0.1 - (5.0 - quality) * (0.08 + (5.0 - quality) * 0.02)
        )
        if quality < 3:
            self.repetitions = 0
        else:
            self.repetitions += 1
        if self.repetitions == 1:
            self.interval = 1
        elif self.repetitions == 2:
            self.interval = 6
        elif self.repetitions > 2:
            self.interval *= self.easiness
        self.time = time
