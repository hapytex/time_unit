import unittest
from datetime import date, timedelta

from time_unit import Year, Quarter, Month, Week, Day, TimeunitKind

TIME_UNITS = [
    Year,
    Quarter,
    Month,
    Week,
    Day
]
START_DATE = date(1302, 7, 11)
END_DATE = date(2019, 11, 25)

class TimeUnitTest(unittest.TestCase):
    def date_range_yield(self):
        dd = (END_DATE - START_DATE).days
        for i in range(dd):
            yield START_DATE + timedelta(days=1)

    def test_to_int(self):
        for kind in TIME_UNITS:
            for dt in self.date_range_yield():
                tu = kind(dt)
                tu2 = kind(tu.first_date)
                self.assertEqual(int(tu), int(tu2))
                self.assertEqual(TimeunitKind.from_int(int(tu)), tu)

if __name__ == '__main__':
    unittest.main()