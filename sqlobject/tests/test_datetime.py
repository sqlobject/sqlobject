from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject import col

########################################
## Date/time columns
########################################

if datetime_available:
    col.default_datetime_implementation = DATETIME_IMPLEMENTATION
    from datetime import date, datetime
    now = datetime.now

    class DateTime1(SQLObject):
        col1 = DateTimeCol()
        col2 = DateCol()

    def test_dateTime():
        setupClass(DateTime1)
        _now = now()
        _today = date.today()
        dt1 = DateTime1(col1=_now, col2=_today)

        assert isinstance(dt1.col1, datetime)
        assert dt1.col1.year == _now.year
        assert dt1.col1.month == _now.month
        assert dt1.col1.day == _now.day
        assert dt1.col1.hour == _now.hour
        assert dt1.col1.minute == _now.minute
        assert dt1.col1.second == int(_now.second)

        assert isinstance(dt1.col2, date)
        assert dt1.col2.year == _today.year
        assert dt1.col2.month == _today.month
        assert dt1.col2.day == _today.day

if mxdatetime_available:
    col.default_datetime_implementation = MXDATETIME_IMPLEMENTATION
    from mx.DateTime import now

    class DateTime2(SQLObject):
        col1 = DateTimeCol()
        col2 = DateCol(dateFormat="%Y-%m-%d %H:%M:%S")
        # mxDateTime does not have a separate date type

    def test_mxDateTime():
        setupClass(DateTime2)
        _now = now()
        dt2 = DateTime2(col1=_now, col2=_now)

        assert isinstance(dt2.col1, col.DateTimeType)
        assert dt2.col1.year == _now.year
        assert dt2.col1.month == _now.month
        assert dt2.col1.day == _now.day
        assert dt2.col1.hour == _now.hour
        assert dt2.col1.minute == _now.minute
        assert dt2.col1.second == int(_now.second)

        assert isinstance(dt2.col2, col.DateTimeType)
        assert dt2.col2.year == _now.year
        assert dt2.col2.month == _now.month
        assert dt2.col2.day == _now.day
        assert dt2.col1.hour == _now.hour
        assert dt2.col1.minute == _now.minute
        assert dt2.col1.second == int(_now.second)
