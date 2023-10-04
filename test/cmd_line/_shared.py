import datetime

_real_datetime = datetime.datetime

class FixNowDatetime:
    def __init__(self, now):
        self._now = now

    def now(self):
        return self._now

    @staticmethod
    def strptime(value, fmt):
        return _real_datetime.strptime(value, fmt)
