"""
General support and utility module.
"""

from datetime import timedelta, tzinfo


class SimpleTZInfo(tzinfo):
    """
    Simple concrete datetime.tzinfo class that handles only
    offset in minutes form UTC.
    """

    def __init__(self, minutes):
        self.minutes = minutes

    def utcoffset(self, dt):
        return timedelta(minutes=self.minutes)

    def dst(self, dt):
        return timedelta()

    def tzname(self, dt):
        if self.minutes < 0:
            sign = '-'
            hours, minutes = divmod(-self.minutes, 60)
        else:
            sign = '+'
            hours, minutes = divmod(self.minutes, 60)
        return '%s%02d:%02d' % (sign, hours, minutes)
