from datetime import time, timedelta
import unittest

from convertish.util import SimpleTZInfo


class TestSimpleTZInfo(unittest.TestCase):

    def test_utcoffset(self):
        self.assertEquals(SimpleTZInfo(60).utcoffset(None), timedelta(minutes=60))
        self.assertEquals(SimpleTZInfo(-60).utcoffset(None), timedelta(minutes=-60))

    def test_dst(self):
        tz = SimpleTZInfo(60)
        self.assertEquals(tz.dst(None), timedelta())

    def test_tzname(self):
        self.assertEquals(SimpleTZInfo(0).tzname(None), "+00:00")
        self.assertEquals(SimpleTZInfo(60).tzname(None), "+01:00")
        self.assertEquals(SimpleTZInfo(90).tzname(None), "+01:30")
        self.assertEquals(SimpleTZInfo(-60).tzname(None), "-01:00")
        self.assertEquals(SimpleTZInfo(-90).tzname(None), "-01:30")

    def test_affect(self):
        self.assertEquals(time(1, 2, 3, 0, SimpleTZInfo(0)).isoformat(), '01:02:03+00:00')
        self.assertEquals(time(1, 2, 3, 0, SimpleTZInfo(90)).isoformat(), '01:02:03+01:30')
        self.assertEquals(time(1, 2, 3, 0, SimpleTZInfo(-90)).isoformat(), '01:02:03-01:30')

