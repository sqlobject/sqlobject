from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject import col
if default_datetime_implementation == DATETIME_IMPLEMENTATION:
    from datetime import datetime
    now = datetime.now
elif default_datetime_implementation == MXDATETIME_IMPLEMENTATION:
    from mx.DateTime import now

########################################
## Date/time columns
########################################

if datetime_available:
    col.default_datetime_implementation = DATETIME_IMPLEMENTATION
    from datetime import date, datetime

    class DateTime1(SQLObject):
        col1 = DateCol()
        col2 = DateTimeCol()

    def test_dateTime():
        setupClass(DateTime1)
        _now = now()
        dt1 = DateTime1(col1=_now, col2=_now)
        assert isinstance(dt1.col1, date)
        assert isinstance(dt1.col2, datetime)

        today_str = _now.strftime("%Y-%m-%d")
        now_str = _now.strftime("%Y-%m-%d %T")
        assert str(dt1.col1) == today_str
        assert str(dt1.col2) == now_str

if mxdatetime_available:
    col.default_datetime_implementation = MXDATETIME_IMPLEMENTATION

    class DateTime2(SQLObject):
        col1 = DateCol()
        col2 = DateTimeCol()

    def test_mxDateTime():
        setupClass(DateTime2)
        _now = now()
        dt2 = DateTime2(col1=_now, col2=_now)
        assert isinstance(dt2.col1, col.DateTimeType)
        assert isinstance(dt2.col2, col.DateTimeType)

        today_str = _now.strftime("%Y-%m-%d 00:00:00.00")
        now_str = _now.strftime("%Y-%m-%d %T.00")
        assert str(dt2.col1) == today_str
        assert str(dt2.col2) == now_str

