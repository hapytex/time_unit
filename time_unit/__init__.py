import math
from datetime import date, datetime, timedelta


def date_from_int(val, div=1):
    val //= div
    d = val % 100
    val //= 100
    m = val % 100
    val //= 100
    return date(val, m, d)


def date_to_int(val, mul=1):
    return mul * (val.year * 10000 + val.month * 100 + val.day)


class TimeunitKindMeta(type):
    kind_int = None
    formatter = None
    _pre_registered = []
    _registered = None
    _multiplier = None

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if cls.kind_int is not None:
            TimeunitKindMeta._pre_registered.append(cls)
            TimeunitKindMeta._registered = None
            TimeunitKindMeta._multiplier = None

    @property
    def unit_register(self):
        result = TimeunitKindMeta._registered
        if result is None:
            result = {
                k.kind_int: k
                for k in TimeunitKindMeta._pre_registered
                if k.kind_int is not None
            }
            TimeunitKindMeta._registered = result
        return result

    @property
    def multiplier(cls):
        result = TimeunitKindMeta._multiplier
        if result is None:
            result = max(1, *[k.kind_int for k in TimeunitKindMeta._pre_registered])
            result = 10 ** math.ceil(math.log10(result))
            TimeunitKindMeta._multiplier = result
        return result

    def __int__(self):
        return self.kind_int

    def __index__(self):
        return int(self)

    def __hash__(self):
        return hash(int(self))

    def __eq__(self, other):
        if isinstance(other, int):
            other = TimeunitKind.unit_register[other]
        return self is other

    def __call__(cls, dt):
        if isinstance(dt, Timeunit):
            dt = dt.dt
        return Timeunit(cls, dt)

    def __lt__(self, other):
        return self.kind_int < other.kind_int

    def from_int(cls, val):
        mul = cls.multiplier
        return TimeunitKind.unit_register[val % mul](date_from_int(val, mul))

    def get_previous(cls, dt):
        if isinstance(dt, Timeunit):
            dt = dt.dt
        dt -= timedelta(days=1)
        return cls(dt)

    def last_day(cls, dt):
        return cls._next(dt) - timedelta(days=1)

    def _next(cls, dt):
        return cls.last_day(dt) + timedelta(days=1)

    def get_next(cls, dt):
        if isinstance(dt, Timeunit):
            dt = dt.dt
        return cls(cls._next(cls.truncate(dt)))

    def to_str(cls, dt):
        return dt.strftime(cls.formatter)

    def truncate(cls, dt):
        return datetime.strptime(cls.to_str(dt), cls.formatter).date()


class TimeunitKind(metaclass=TimeunitKindMeta):
    kind_int = None
    formatter = None

class Year(TimeunitKind):
    kind_int = 1
    formatter = "%Y"

    @classmethod
    def _next(cls, dt):
        return date(dt.year + 1, 1, 1)


class Quarter(TimeunitKind):
    kind_int = 3

    @classmethod
    def to_str(cls, dt):
        return f"{dt.year}Q{dt.month//3}"

    @classmethod
    def truncate(cls, dt):
        return date(dt.year, 3 * ((dt.month - 1) // 3) + 1, 1)

    @classmethod
    def _next(cls, dt):
        q2 = 3 * (dt.month + 2) // 3 + 1
        if q2 == 13:
            return date(dt.year + 1, 1, 1)
        return date(dt.year, q2, 1)


class Month(TimeunitKind):
    kind_int = 5
    formatter = "%YM%m"

    @classmethod
    def _next(cls, dt):
        m2 = dt.month + 1
        if m2 > 12:
            return date(dt.year + 1, 1, 1)
        else:
            return date(dt.year, m2, 1)


class Week(TimeunitKind):
    kind_int = 7
    formatter = "%YW%W"

    @classmethod
    def truncate(cls, dt):
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt - timedelta(days=dt.weekday())

    @classmethod
    def _next(cls, dt):
        return dt + timedelta(days=7)


class Day(TimeunitKind):
    kind_int = 9
    formatter = "%Y-%m-%d"

    @classmethod
    def _next(self, dt):
        return dt + timedelta(days=1)


class Timeunit:
    def __init__(self, kind, dt):
        if isinstance(kind, int):
            kind = TimeunitKind.unit_register[kind]
        self.kind = kind
        self.dt = kind.truncate(dt)

    @property
    def previous(self):
        return self.kind.get_previous(self.dt)

    @property
    def first_date(self):
        return self.dt

    @property
    def last_date(self):
        return self.kind.last_day(self.dt)

    @property
    def date_range(self):
        return self.dt, self.last_date

    @property
    def ancestors(self):
        result = self
        while True:
            result = result.previous
            yield result

    @property
    def successors(self):
        result = self
        while True:
            result = result.next
            yield result

    def __len__(self):
        return (self.next.dt - self.dt).days

    def __iter__(self):
        dt = self.dt
        end = self.next.dt
        ONE_DAY = timedelta(days=1)
        while dt < end:
            yield dt
            dt += ONE_DAY

    @property
    def next(self):
        return self.kind.get_next(self.dt)

    def __index__(self):
        return int(self)

    def __eq__(self, other):
        if isinstance(other, int):
            other = TimeunitKind.from_int(other)
        return self.kind == other.kind and self.dt == other.dt

    def __lt__(self, other):
        return int(self) < int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __int__(self):
        return date_to_int(self.dt, self.kind.multiplier) + self.kind.kind_int

    def __hash__(self):
        return hash(int(self))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.kind.__qualname__}, {self.dt!r})"

    @classmethod
    def _get_range(cls, item):
        if isinstance(item, date):
            return item, item
        elif isinstance(item, Timeunit):
            return item.date_range
        # try to make a range
        try:
            dt0, dt1 = item
            if isinstance(dt0, date) and isinstance(dt1, date):
                return item
        except TypeError:
            raise TypeError('Item {item!r} has no date range.')

    def overlaps_with(self, item):
        frm0, to0 = self._get_range(item)
        frm, to = self.date_range
        return to >= frm0 and to0 >= frm

    def __contains__(self, item):
        frm0, to0 = self._get_range(item)
        frm, to = self.date_range
        return frm <= frm0 and to0 <= to

    def __str__(self):
        return self.kind.to_str(self.dt)