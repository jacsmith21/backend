import unittest

import utils


class TestUtils(unittest.TestCase):
    def test_date_to_datetime(self):
        dt = utils.date_to_datetime('2018-07-04')
        assert dt.day == 4
        assert dt.month == 7
        assert dt.year == 2018

    def test_unix_time(self):
        dt = utils.date_to_datetime('2018-07-04')
        assert utils.unix_time(dt) == 1530662400
