from datetime import datetime, date, time
import pytest

from sqlobject import SQLObject
from sqlobject import col
from sqlobject.col import DateCol, DateTimeCol, TimeCol, use_microseconds, \
    DATETIME_IMPLEMENTATION, MXDATETIME_IMPLEMENTATION, mxdatetime_available, \
    ZOPE_DATETIME_IMPLEMENTATION, zope_datetime_available
from sqlobject.tests.dbtest import getConnection, setupClass
from sqlobject.converters import pendulumDateTimeType

########################################
# Date/time columns
########################################


col.default_datetime_implementation = DATETIME_IMPLEMENTATION


class DateTime1(SQLObject):
    col1 = DateTimeCol()
    col2 = DateCol()
    col3 = TimeCol()


def test_dateTime():
    setupClass(DateTime1)
    _now = datetime.now().replace(microsecond=0)
    dt1 = DateTime1(col1=_now, col2=_now, col3=_now.time())

    assert isinstance(dt1.col1, datetime)
    assert dt1.col1.year == _now.year
    assert dt1.col1.month == _now.month
    assert dt1.col1.day == _now.day
    assert dt1.col1.hour == _now.hour
    assert dt1.col1.minute == _now.minute
    assert dt1.col1.second == _now.second

    assert isinstance(dt1.col2, date)
    assert not isinstance(dt1.col2, datetime)
    assert dt1.col2.year == _now.year
    assert dt1.col2.month == _now.month
    assert dt1.col2.day == _now.day

    assert isinstance(dt1.col3, time)
    assert dt1.col3.hour == _now.hour
    assert dt1.col3.minute == _now.minute
    assert dt1.col3.second == _now.second


def test_microseconds():
    connection = getConnection()
    if not hasattr(connection, 'can_use_microseconds') or \
            not connection.can_use_microseconds():
        pytest.skip(
            "The database doesn't support microseconds; "
            "microseconds are supported by MariaDB since version 5.3.0, "
            "by MySQL since version 5.6.4, "
            "by MSSQL since MS SQL Server 2008.")

    setupClass(DateTime1)
    _now = datetime.now()
    dt1 = DateTime1(col1=_now, col2=_now, col3=_now.time())

    assert dt1.col1.microsecond == _now.microsecond
    assert dt1.col3.microsecond == _now.microsecond

    use_microseconds(False)
    setupClass(DateTime1)
    _now = datetime.now()
    dt1 = DateTime1(col1=_now, col2=_now, col3=_now.time())

    assert dt1.col1.microsecond == 0
    assert dt1.col3.microsecond == 0

    use_microseconds(True)
    setupClass(DateTime1)
    _now = datetime.now()
    dt1 = DateTime1(col1=_now, col2=_now, col3=_now.time())

    assert dt1.col1.microsecond == _now.microsecond
    assert dt1.col3.microsecond == _now.microsecond

if mxdatetime_available:
    col.default_datetime_implementation = MXDATETIME_IMPLEMENTATION
    from mx.DateTime import now as mx_now, Time as mxTime

    dateFormat = None  # use default
    try:
        connection = getConnection()
    except AttributeError:
        # The module was imported during documentation building
        pass
    else:
        if connection.dbName == "sqlite":
            if connection.using_sqlite2:
                # mxDateTime sends and PySQLite2 returns
                # full date/time for dates
                dateFormat = "%Y-%m-%d %H:%M:%S.%f"

    class DateTime2(SQLObject):
        col1 = DateTimeCol()
        col2 = DateCol(dateFormat=dateFormat)
        col3 = TimeCol()

    def test_mxDateTime():
        setupClass(DateTime2)
        _now = mx_now()
        dt2 = DateTime2(col1=_now, col2=_now.pydate(),
                        col3=mxTime(_now.hour, _now.minute, _now.second))

        assert isinstance(dt2.col1, col.mxDateTimeType)
        assert dt2.col1.year == _now.year
        assert dt2.col1.month == _now.month
        assert dt2.col1.day == _now.day
        assert dt2.col1.hour == _now.hour
        assert dt2.col1.minute == _now.minute
        assert dt2.col1.second == int(_now.second)

        assert isinstance(dt2.col2, col.mxDateTimeType)
        assert dt2.col2.year == _now.year
        assert dt2.col2.month == _now.month
        assert dt2.col2.day == _now.day
        assert dt2.col2.hour == 0
        assert dt2.col2.minute == 0
        assert dt2.col2.second == 0

        assert isinstance(dt2.col3, (col.mxDateTimeType, col.mxTimeType))
        assert dt2.col3.hour == _now.hour
        assert dt2.col3.minute == _now.minute
        assert dt2.col3.second == int(_now.second)

if pendulumDateTimeType:
    col.default_datetime_implementation = DATETIME_IMPLEMENTATION
    import pendulum

    class DateTimePendulum(SQLObject):
        col1 = DateTimeCol()

    def test_PendulumDateTime():
        setupClass(DateTimePendulum)
        _now = pendulum.now()
        dtp = DateTimePendulum(col1=_now)

        assert isinstance(dtp.col1, datetime)
        assert dtp.col1.year == _now.year
        assert dtp.col1.month == _now.month
        assert dtp.col1.day == _now.day
        assert dtp.col1.hour == _now.hour
        assert dtp.col1.minute == _now.minute
        assert int(dtp.col1.second) == int(_now.second)


if zope_datetime_available:
    col.default_datetime_implementation = ZOPE_DATETIME_IMPLEMENTATION
    from DateTime import DateTime as zopeDateTime

    class DateTime3(SQLObject):
        col1 = DateTimeCol()

    def test_ZopeDateTime():
        setupClass(DateTime3)
        _now = zopeDateTime()
        dt3 = DateTime3(col1=_now)

        assert isinstance(dt3.col1, col.zopeDateTimeType)
        assert dt3.col1.year() == _now.year()
        assert dt3.col1.month() == _now.month()
        assert dt3.col1.day() == _now.day()
        assert dt3.col1.hour() == _now.hour()
        assert dt3.col1.minute() == _now.minute()
        assert int(dt3.col1.second()) == int(_now.second())
