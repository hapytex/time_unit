# `unit_of_time`

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unit_of_time)](https://pypi.org/project/unit_of_time/)


`unit_of_time` is a small package to represents time ranges through an `int`, this means we can easily store these, for
example in a database. It also offers functions to determine the previous and next time range.

## Time units

The package by default comes with a year, quarter, month, week and day as time units. We want to be able to convert
a certain week into an int, and back. For this, we have defined the following rule:

 - a time range should encode to one integer, *not* per se the other way around;
 - the time ranges should be orderable such that we can easily order and sort items in the database; and
 - it should be easy for humans to read the integers.

For this we have defined the following format:

```
YYYYMMDDK
```

Here YYYY-MM-DD is the *start date* of the time range, and K is the "kind" of time range. The longer a time unit, the lower its kind.

So a year for example has kind `1`, this means that we encode the year 2025 as `202501011`, the month january 2025 is encoded as `202501015`.

If we thus order the time units, we first sort on the start of the time unit, and the ordering will put longer time units first, so the "year 2025 starts 'earlier' than the quarter 2025Q1 which starts earlier than 2025-01".

## Utility functions

The package provides some utility functions to make working with the time units more convenient.

### Moving forward and backward

For example when we construct a year with

```python3
year1958 = Year(date(1958, 3, 25))
```

we can go to the next and previous year with:

```python3
year1959 = year1958.next
year1957 = year1958.previous
```

one can also use `.ancestors` and `.successors` which are generators that will keep proposing previous and next time units respectively, so we can walk over the years since 1958 with:

```python3
for year in year1958.successors:
  print(year)
```

### Membership checks

We can also determine if a date, or another time range is fully enclosed by another one, for example:

```python3
Month(date(1958, 3, 25)) in Year(date(1958, 3, 25))  # True
Month(date(2019, 11, 25)) in Year(date(1958, 3, 25))  # False
```

or check if there is overlap between two time units, especially since weeks are not always fully enclosed by the month, quarter, etc. when the week starts or ends. For example:

```python3
Week(date(1957, 12, 31)).overlaps_with(Year(date(1958, 1, 1)))  # True
```

since the week with 1957-12-31 starts on December 30th.

### Ordering

We can also check if one time unit starts before another time unit if these are of the same kind, like:

```python3
Week(date(1957, 12, 31)) <= Week(date(1958, 3, 25))
```

### Time units as a collection of dates

A time unit itself is iterable: it will yield all dates contained by the time unit. For example we can get all dates of `1958Q1` with:

```python3
for dt in Quarter(date(1958, 3, 25)):
  print(dt)  # 1958-01-01 to 1958-03-31
```

we can also convert such collection to a list.

### Hash and index

A time unit is hashable, it uses the `int` representation as hash. It is also indexable, and uses the `int` representation.

We can thus make a (very) long list, and work with:

```python3
specials_unit_of_times = [False] * 202512319
specials_unit_of_times[Day(date(1958, 3, 25))] = True
```

we can even use this to slice, although it probably is not very useful.

## Registering a new time unit

We can register a new time unit, for example a decade with:

```python3
class Decade(TimeunitKind):
    kind_int = 0
    formatter = "%Ys"

    @classmethod
    def truncate(cls, dt):
        return date(dt.year - dt.year % 10, 1, 1)

    @classmethod
    def _next(cls, dt):
        return date(dt.year + 10, 1, 1)
```

Subclassing `TimeunitKind` will automatically register it. One has to fill in the `kind_int`, which is an integer, preferrably between `0` and `9`, although one can register outside the range. If that is the case, the "kind" will take two or more digits when converting to an int.

One can also implment a formatter. This is strictly speaking not necessary, since one can also implement a `.to_str()` method:

```python3
class Decade(TimeunitKind):
    kind_int = 0
    
    def to_str(cls, dt):
        return dt.strftime('%Ys')

    # ...
```

this might be useful if the formatting is more advanced than what Python's date formatter can handle.

Furthermore, one implements the `.truncate(..)` class method to convert a date to the start of the date range, and the `_next(..)` which returns the first date for the next decade.

With these functions, we have registered a new time unit.

## Pre-installed time units

The package ships with the following time units:

- **1**: year;
- **3**: quarter;
- **5**: month;
- **7**: week; and
- **9**: day.

There is deliberately always one integer between the two time units, such that one can always put a customized one between any of the two.

`195803259 – 201911259`
