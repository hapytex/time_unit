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
                self.assertLess(tu.previous, tu)
                self.assertLess(tu, tu.next)
                self.assertLess(int(tu), int(tu.next))
                self.assertLess(int(tu.previous), int(tu))
                self.assertEqual(TimeunitKind.from_int(int(tu)), tu)
                self.assertIn(dt, tu)
                self.assertIn(dt, list(tu))
                self.assertIn(tu, tu)
                self.assertNotIn(dt, tu.next)
                self.assertNotIn(dt, tu.previous)
                self.assertNotIn(tu, tu.next)
                self.assertNotIn(tu, tu.previous)
                self.assertNotIn(tu.previous, tu)
                self.assertNotIn(tu.next, tu)
                self.assertTrue(tu.overlaps_with(tu))
                self.assertFalse(tu.next.overlaps_with(tu))
                self.assertFalse(tu.previous.overlaps_with(tu))
                self.assertFalse(tu.overlaps_with(tu.next))
                self.assertFalse(tu.overlaps_with(tu.previous))
                self.assertLess(tu.last_date, tu.next.first_date)
                self.assertLess(tu.previous.last_date, tu.first_date)
                self.assertEqual((tu.next.first_date - tu.last_date), timedelta(days=1))
                self.assertEqual((tu.first_date - tu.previous.last_date), timedelta(days=1))

    def test_hierarchy(self):
        for i, superkind in enumerate(TIME_UNITS, 1):
            for kind in TIME_UNITS[i:]:
                for dt in self.date_range_yield():
                    stu = superkind(dt)
                    tu = kind(dt)
                    self.assertLess(len(tu), len(stu))
                    self.assertNotEqual(stu, tu)
                    self.assertNotEqual(int(stu), int(tu))
                    self.assertTrue(stu.overlaps_with(tu))
                    self.assertTrue(tu.overlaps_with(stu))

if __name__ == '__main__':
    unittest.main()