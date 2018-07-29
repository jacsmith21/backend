import unittest

import openpyxl

import utils

DATE = '2018-07-04'


class TestUtils(unittest.TestCase):
    def test_date_to_datetime(self):
        dt = utils.date_to_datetime(DATE)
        assert dt.day == 4
        assert dt.month == 7
        assert dt.year == 2018

    def test_unix_time(self):
        dt = utils.date_to_datetime(DATE)
        assert utils.unix_time(dt) == 1530662400

    def test_datetime_to_date(self):
        dt = utils.date_to_datetime(DATE)
        assert utils.datetime_to_date(dt) == DATE

    def test_unix_to_date(self):
        dt = utils.date_to_datetime(DATE)
        unix = utils.unix_time(dt)
        assert utils.unix_to_date(unix) == DATE

    def test_export(self):
        with utils.export({'number': 'JACOB'}) as path:
            workbook = openpyxl.load_workbook(path)
            sheet = workbook['JACOB']
            assert sheet['C3'].internal_value == 'JACOB'
            workbook.close()

    def test_crange(self):
        assert list(utils.crange('A', 'D')) == ['A', 'B', 'C', 'D']

    def test_make_cells(self):
        assert list(utils.make_cells('A1', 'C1')) == ['A1', 'B1', 'C1']
        assert list(utils.make_cells('A1', 'A3')) == ['A1', 'A2', 'A3']
