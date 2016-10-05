import pytest
from sqlobject import AND, IntCol, OR, SQLObject, UnicodeCol
from sqlobject.compat import PY2
from sqlobject.tests.dbtest import raises, setupClass


########################################
# Unicode columns
########################################


class SOTestUnicode(SQLObject):
    count = IntCol(alternateID=True)
    col1 = UnicodeCol(alternateID=True, length=100)
    if PY2:
        col2 = UnicodeCol(dbEncoding='latin1')


data = [u'\u00f0', u'test', 'ascii test']
items = []


def setup():
    global items
    items = []
    setupClass(SOTestUnicode)
    if SOTestUnicode._connection.dbName == 'postgres':
        if PY2:
            dbEncoding = 'latin1'
        else:
            dbEncoding = 'utf8'
        SOTestUnicode._connection.query(
            'SET client_encoding TO %s' % dbEncoding)
    if PY2:
        for i, s in enumerate(data):
            items.append(SOTestUnicode(count=i, col1=s, col2=s))
    else:
        for i, s in enumerate(data):
            items.append(SOTestUnicode(count=i, col1=s))


def test_create():
    setup()
    for s, item in zip(data, items):
        assert item.col1 == s
        if PY2:
            assert item.col2 == s

    conn = SOTestUnicode._connection
    if PY2:
        rows = conn.queryAll("""
        SELECT count, col1, col2
        FROM so_test_unicode
        ORDER BY count
        """)
        for count, col1, col2 in rows:
            assert data[count].encode('utf-8') == col1
            assert data[count].encode('latin1') == col2
    else:
        rows = conn.queryAll("""
        SELECT count, col1
        FROM so_test_unicode
        ORDER BY count
        """)
        # On python 3, everthings already decoded to unicode
        for count, col1 in rows:
            assert data[count] == col1


def _test_select():
    for i, value in enumerate(data):
        rows = list(SOTestUnicode.select(SOTestUnicode.q.col1 == value))
        assert len(rows) == 1
        if PY2:
            rows = list(SOTestUnicode.select(SOTestUnicode.q.col2 == value))
            assert len(rows) == 1
            rows = list(SOTestUnicode.select(AND(
                SOTestUnicode.q.col1 == value,
                SOTestUnicode.q.col2 == value
            )))
            assert len(rows) == 1
        rows = list(SOTestUnicode.selectBy(col1=value))
        assert len(rows) == 1
        if PY2:
            rows = list(SOTestUnicode.selectBy(col2=value))
            assert len(rows) == 1
            rows = list(SOTestUnicode.selectBy(col1=value, col2=value))
            assert len(rows) == 1
        row = SOTestUnicode.byCol1(value)
        assert row.count == i
    if PY2:
        rows = list(SOTestUnicode.select(OR(
            SOTestUnicode.q.col1 == u'\u00f0',
            SOTestUnicode.q.col2 == u'test'
        )))
        assert len(rows) == 2
        rows = list(SOTestUnicode.selectBy(col1=u'\u00f0', col2=u'test'))
        assert len(rows) == 0

    # starts/endswith/contains
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col1.startswith("test")))
    assert len(rows) == 1
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col1.endswith("test")))
    assert len(rows) == 2
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col1.contains("test")))
    assert len(rows) == 2
    rows = list(SOTestUnicode.select(
        SOTestUnicode.q.col1.startswith(u"\u00f0")))
    assert len(rows) == 1
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col1.endswith(u"\u00f0")))
    assert len(rows) == 1
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col1.contains(u"\u00f0")))
    assert len(rows) == 1


def test_select():
    setup()
    _test_select()


def test_dbEncoding():
    if not PY2:
        # Python 3 mostly ignores dbEncoding
        pytest.skip("This test is for python 2")
    setup()
    SOTestUnicode.sqlmeta.dbEncoding = 'utf-8'
    _test_select()
    SOTestUnicode.sqlmeta.dbEncoding = 'latin-1'
    raises(AssertionError, _test_select)
    SOTestUnicode.sqlmeta.dbEncoding = 'ascii'
    raises(UnicodeEncodeError, _test_select)
    SOTestUnicode.sqlmeta.dbEncoding = None

    SOTestUnicode._connection.dbEncoding = 'utf-8'
    _test_select()
    SOTestUnicode._connection.dbEncoding = 'latin-1'
    raises(AssertionError, _test_select)
    SOTestUnicode._connection.dbEncoding = 'ascii'
    raises(UnicodeEncodeError, _test_select)
    del SOTestUnicode.sqlmeta.dbEncoding
    SOTestUnicode._connection.dbEncoding = 'utf-8'
