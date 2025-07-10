import unittest
from datetime import date, datetime, time, timedelta

from time_unit import Year, Quarter, Month, Week, Day, TimeunitKind, Timeunit


class Decade(TimeunitKind):
    kind_int = 0
    formatter = '%Ys'

    @classmethod
    def truncate(cls, dt):
        dt = cls.truncate(dt)
        return date(10 * (dt.year // 10), 1, 1)

    @classmethod
    def last_day(cls, dt):
        return date(dt.year + 10, 1, 1) - timedelta(days=1)


TIME_UNITS = [Decade, Year, Quarter, Month, Week, Day]
START_DATE = date(1302, 7, 11)
END_DATE = date(2019, 11, 25)


class TimeUnitTest(unittest.TestCase):
    def date_range_yield(self):
        dd = (END_DATE - START_DATE).days
        for i in range(dd):
            yield START_DATE + timedelta(days=i)

    def test_to_int(self):
        prev_set = set()
        prev_name = set()
        cur_set = set()
        cur_name = set()
        d = [False] * 202101019
        for kind in TIME_UNITS:
            prev_name.update(cur_name)
            prev_set.update(cur_set)
            cur_set = set()
            cur_name = set()
            for dt in self.date_range_yield():
                with self.subTest(kind=kind, dt=dt):
                    tu = kind(dt)
                    self.assertEqual(tu, kind(datetime.combine(dt, time(14, 25))))
                    self.assertEqual(d[tu], tu in cur_set)
                    self.assertEqual(d[tu], int(tu) in cur_set)
                    d[tu] = True
                    cur_set.add(int(tu))
                    cur_name.add(str(tu))
                    self.assertNotIn(int(tu), prev_set)
                    self.assertNotIn(str(tu), prev_name)
                    tu2 = kind(tu.first_date)
                    self.assertEqual(Timeunit(int(tu.kind), tu.dt), tu)
                    self.assertEqual(int(tu), int(tu2))
                    self.assertEqual(repr(tu), repr(tu2))
                    self.assertEqual(kind(tu), tu)
                    self.assertEqual(tu == tu2, str(tu) == str(tu2))
                    self.assertNotEqual(str(tu), str(tu.next))
                    self.assertNotEqual(str(tu.previous), str(tu))
                    self.assertEqual(tu.next.previous, tu)
                    self.assertEqual(tu.previous.next, tu)
                    self.assertLess(tu.previous, tu)
                    self.assertLess(tu, tu.next)
                    self.assertLessEqual(tu.previous, tu)
                    self.assertLessEqual(tu, tu.next)
                    self.assertGreater(tu, tu.previous)
                    self.assertGreater(tu.next, tu)
                    self.assertGreaterEqual(tu, tu.previous)
                    self.assertGreaterEqual(tu.next, tu)
                    self.assertLess(int(tu), int(tu.next))
                    self.assertLess(int(tu.previous), int(tu))
                    self.assertLessEqual(tu.dt, tu.last_date)
                    self.assertEqual(TimeunitKind.from_int(int(tu)), tu)
                    self.assertIn(dt, tu)
                    self.assertIn((dt, dt), tu)
                    self.assertIn((tu.first_date, tu.last_date), tu)
                    with self.assertRaises(TypeError):
                        self.assertIn(1425, tu)
                    self.assertIn(dt, list(tu))
                    self.assertEqual(len(tu), len(list(tu)))
                    ance = tu.ancestors
                    self.assertEqual(tu.previous, next(ance))
                    self.assertEqual(tu.previous.previous, next(ance))
                    succ = tu.successors
                    self.assertEqual(tu.next, next(succ))
                    self.assertEqual(tu.next.next, next(succ))
                    self.assertEqual(tu, tu)
                    self.assertLessEqual(tu, tu)
                    self.assertGreaterEqual(tu, tu)
                    self.assertIn(tu, tu)
                    self.assertNotIn(dt, tu.next)
                    self.assertNotIn(dt, tu.previous)
                    self.assertNotIn(tu, tu.next)
                    self.assertEqual(tu.previous, kind.get_previous(tu))
                    self.assertEqual(tu.next, kind.get_next(tu))
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
                    self.assertEqual(
                        (tu.next.first_date - tu.last_date), timedelta(days=1)
                    )
                    self.assertEqual(
                        (tu.first_date - tu.previous.last_date), timedelta(days=1)
                    )

    def test_hierarchy(self):
        for i, superkind in enumerate(TIME_UNITS, 1):
            for kind in TIME_UNITS[i:]:
                for dt in self.date_range_yield():
                    with self.subTest(superkind=superkind, kind=kind, dt=dt):
                        stu = superkind(dt)
                        tu = kind(dt)
                        self.assertLess(len(tu), len(stu))
                        self.assertLess(int(stu.previous), int(tu))
                        self.assertLess(int(tu), int(stu.next))
                        self.assertNotEqual(stu, tu)
                        self.assertNotEqual(str(stu), str(tu))
                        self.assertNotEqual(repr(stu), repr(tu))
                        self.assertNotEqual(int(stu), int(tu))
                        self.assertTrue(stu.overlaps_with(tu))
                        self.assertTrue(tu.overlaps_with(stu))

    def test_kinds(self):
        seen = set()
        d = [False] * 10
        for i, kind in enumerate(TIME_UNITS, 1):
            self.assertEqual(kind, kind)
            self.assertEqual(kind, kind.kind_int)
            self.assertEqual(kind.kind_int, kind)
            self.assertEqual(d[kind], kind in seen)
            d[kind] = True
            self.assertNotIn(kind, seen)
            seen.add(kind)
            for kind2 in TIME_UNITS[i:]:
                self.assertLess(kind, kind2)


if __name__ == '__main__':
    unittest.main()
