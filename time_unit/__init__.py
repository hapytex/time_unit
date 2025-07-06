import math
from datetime import date, datetime, timedelta


def date_from_int(val, div=1):
    """
    Convert an integer in YYYYMMDD format to a `date` object, optionally scaling down by a divisor.
    
    Parameters:
    	val (int): Integer representing a date in YYYYMMDD format, possibly scaled.
    	div (int, optional): Divisor to scale down the input integer before extracting date components. Defaults to 1.
    
    Returns:
    	date: Corresponding `date` object.
    """
    val //= div
    d = val % 100
    val //= 100
    m = val % 100
    val //= 100
    return date(val, m, d)


def date_to_int(val, mul=1):
    """
    Convert a date object to an integer in the format YYYYMMDD, optionally scaled by a multiplier.
    
    Parameters:
        val (date): The date to convert.
        mul (int, optional): Multiplier to scale the resulting integer. Defaults to 1.
    
    Returns:
        int: The integer representation of the date, scaled by the multiplier.
    """
    return mul * (val.year * 10000 + val.month * 100 + val.day)


class TimeunitKindMeta(type):
    kind_int = None
    formatter = None
    _pre_registered = []
    _registered = None
    _multiplier = None

    def __init__(cls, name, bases, attrs):
        """
        Initializes a TimeunitKind subclass and registers it if it defines a kind integer.
        
        This method appends the subclass to the pre-registration list if `kind_int` is set, and resets the cached registration and multiplier to ensure correct encoding of time unit kinds.
        """
        super().__init__(name, bases, attrs)
        if cls.kind_int is not None:
            TimeunitKindMeta._pre_registered.append(cls)
            TimeunitKindMeta._registered = None
            TimeunitKindMeta._multiplier = None

    @property
    def unit_register(self):
        """
        Returns the dictionary mapping registered time unit kind integers to their corresponding classes.
        
        This property lazily initializes the mapping from `kind_int` values to `TimeunitKind` subclasses if it has not already been built.
        """
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
        """
        Returns the scaling multiplier used to uniquely encode date and kind integers for all registered time unit kinds.
        
        The multiplier is computed as the next power of 10 greater than or equal to the largest `kind_int` among registered kinds, ensuring unique integer representations when combining dates and kind identifiers.
        Returns:
            int: The computed multiplier value.
        """
        result = TimeunitKindMeta._multiplier
        if result is None:
            result = max(1, *[k.kind_int for k in TimeunitKindMeta._pre_registered])
            result = 10 ** math.ceil(math.log10(result))
            TimeunitKindMeta._multiplier = result
        return result

    def __int__(self):
        """
        Return the integer identifier associated with this time unit kind.
        """
        return self.kind_int

    def __index__(self):
        """
        Return the integer representation of the time unit for use in index operations.
        """
        return int(self)

    def __hash__(self):
        """
        Return the hash value of the time unit, based on its unique integer representation.
        """
        return hash(int(self))

    def __call__(cls, dt):
        """
        Creates a `Timeunit` instance of this kind from a date, datetime, or another `Timeunit`.
        
        If a `Timeunit` is provided, its date is extracted and used.
        """
        if isinstance(dt, Timeunit):
            dt = dt.dt
        return Timeunit(cls, dt)

    def __lt__(self, other):
        """
        Return True if this time unit kind has a lower precedence than another based on its kind integer.
        """
        return self.kind_int < other.kind_int

    def from_int(cls, val):
        """
        Creates a TimeunitKind instance from an integer encoding both the date and kind.
        
        The integer is decoded using the class's multiplier to extract the kind and date components.
        """
        mul = cls.multiplier
        return TimeunitKind.unit_register[val % mul](date_from_int(val, mul))

    def get_previous(cls, dt):
        """
        Return the previous time unit instance of this kind before the given date.
        
        If a `Timeunit` is provided, its date is used. The previous unit is determined by subtracting one day from the input date and truncating to the start of the corresponding time unit kind.
        
        Parameters:
        	dt: A `date`, `datetime`, or `Timeunit` to find the previous time unit for.
        
        Returns:
        	A new instance of this time unit kind representing the previous unit.
        """
        if isinstance(dt, Timeunit):
            dt = dt.dt
        dt -= timedelta(days=1)
        return cls(dt)

    def last_day(cls, dt):
        return cls._next(dt) - timedelta(days=1)

    def _next(cls, dt):
        return cls._last_day(dt) + timedelta(days=1)

    def get_next(cls, dt):
        if isinstance(dt, Timeunit):
            dt = dt.dt
        return cls(cls._next(cls.truncate(dt)))

    def truncate(cls, dt):
        raise NotImplementedError()

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
        """
        Return the first day of the next quarter following the given date.
        
        Parameters:
        	dt (date): The reference date.
        
        Returns:
        	date: The first day of the next quarter.
        """
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
            kind = TimeunitKindMeta._registered[kind]
        self.kind = kind
        self.dt = kind.truncate(dt)

    @property
    def previous(self):
        """
        Return the previous time unit instance of the same kind.
        
        Returns:
        	Timeunit: The immediately preceding time unit of the same kind as this instance.
        """
        return self.kind.get_previous(self.dt)

    @property
    def first_date(self):
        """
        Returns the first date of the time unit, corresponding to the start of the represented period.
        """
        return self.dt

    @property
    def last_date(self):
        """
        Return the last date included in this time unit.
        
        Returns:
            date: The final date covered by this time unit instance.
        """
        return self.kind.last_day(self.dt)

    @property
    def date_range(self):
        """
        Return the start and end dates of this time unit as a tuple.
        
        Returns:
            (date, date): A tuple containing the first and last dates of the time unit.
        """
        return self.dt, self.last_date

    @property
    def ancestors(self):
        """
        Yields an infinite sequence of preceding time units of the same kind.
        
        Each yielded value is the previous time unit, moving backward in time indefinitely.
        """
        result = self.previous
        while True:
            yield result
            result = result.previous

    @property
    def successors(self):
        result = self.next
        while True:
            yield result
            result = result.next

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
        """
        Returns the next time unit instance of the same kind following this one.
        """
        return self.kind.get_next(self.dt)

    def __index__(self):
        """
        Return the integer representation of the time unit for use in index operations.
        """
        return int(self)

    def __eq__(self, other):
        """
        Return True if this time unit is equal to another, based on kind and date.
        """
        return self.kind == other.kind and self.dt == other.dt

    def __lt__(self, other):
        return int(self) < int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __ge__(self, other):
        """
        Return True if this time unit is greater than or equal to another, based on their integer representations.
        """
        return int(self) >= int(other)

    def __int__(self):
        """
        Return the unique integer encoding of this time unit, combining its truncated date and kind.
        
        The encoding uses the kind's multiplier to ensure uniqueness across different time unit kinds.
        """
        return date_to_int(self.dt, self.kind.multiplier) + self.kind.kind_int

    def __hash__(self):
        """
        Return the hash value of the time unit, based on its unique integer representation.
        """
        return hash(int(self))

    def __repr__(self):
        """
        Return a string representation of the Timeunit instance, showing its class name, kind, and associated date.
        """
        return f"{self.__class__.__name}({self.kind.__qualname__}, {self.dt!r})"

    @classmethod
    def _get_range(cls, item):
        """
        Return the date range represented by the given item.
        
        If the item is a `date`, returns a tuple with the date as both start and end.
        If the item is a `Timeunit`, returns its date range.
        Raises a `TypeError` if the item does not represent a date range.
        """
        if isinstance(item, date):
            return item, item
        elif isinstance(item, Timeunit):
            return item.date_range
        raise TypeError('Item {item!r} has no date range.')

    def overlaps_with(self, item):
        """
        Determine whether this time unit overlaps with another time unit or date range.
        
        Parameters:
            item: A date, Timeunit, or tuple representing a date range to check for overlap.
        
        Returns:
            bool: True if there is any overlap between this time unit and the specified item; otherwise, False.
        """
        frm0, to0 = self._get_range(item)
        frm, to = self.date_range
        return to >= frm0 and to0 >= frm

    def __contains__(self, item):
        """
        Check if a date or time unit is fully contained within this time unit.
        
        Returns:
            bool: True if the given date or time unit falls entirely within the range of this time unit, otherwise False.
        """
        frm0, to0 = self._get_range(item)
        frm, to = self.date_range
        return frm <= frm0 and to0 <= to

    def __str__(self):
        """
        Return the string representation of this time unit using its kind's formatting rules.
        """
        return self.kind.to_str(self.dt)
