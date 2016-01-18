import py.test
from sqlobject import *
from sqlobject.compat import PY2
from sqlobject.tests.dbtest import *


########################################
# Unicode columns
########################################


class TestUnicode(SQLObject):
    count = IntCol(alternateID=True)
    col1 = UnicodeCol(alternateID=True, length=100)
    if PY2:
        col2 = UnicodeCol(dbEncoding='latin1')


data = [u'\u00f0', u'test', 'ascii test']
items = []


def setup():
    global items
    items = []
    setupClass(TestUnicode)
    if TestUnicode._connection.dbName == 'postgres':
        if PY2:
            dbEncoding = 'latin1'
        else:
            dbEncoding = 'utf8'
        TestUnicode._connection.query('SET client_encoding TO %s' % dbEncoding)
    if PY2:
        for i, s in enumerate(data):
            items.append(TestUnicode(count=i, col1=s, col2=s))
    else:
        for i, s in enumerate(data):
            items.append(TestUnicode(count=i, col1=s))


def test_create():
    setup()
    for s, item in zip(data, items):
        assert item.col1 == s
        if PY2:
            assert item.col2 == s

    conn = TestUnicode._connection
    if PY2:
        rows = conn.queryAll("""
        SELECT count, col1, col2
        FROM test_unicode
        ORDER BY count
        """)
        for count, col1, col2 in rows:
            assert data[count].encode('utf-8') == col1
            assert data[count].encode('latin1') == col2
    else:
        rows = conn.queryAll("""
        SELECT count, col1
        FROM test_unicode
        ORDER BY count
        """)
        # On python 3, everthings already decoded to unicode
        for count, col1 in rows:
            assert data[count] == col1


def _test_select():
    for i, value in enumerate(data):
        rows = list(TestUnicode.select(TestUnicode.q.col1 == value))
        assert len(rows) == 1
        if PY2:
            rows = list(TestUnicode.select(TestUnicode.q.col2 == value))
            assert len(rows) == 1
            rows = list(TestUnicode.select(AND(
                TestUnicode.q.col1 == value,
                TestUnicode.q.col2 == value
            )))
            assert len(rows) == 1
        rows = list(TestUnicode.selectBy(col1=value))
        assert len(rows) == 1
        if PY2:
            rows = list(TestUnicode.selectBy(col2=value))
            assert len(rows) == 1
            rows = list(TestUnicode.selectBy(col1=value, col2=value))
            assert len(rows) == 1
        row = TestUnicode.byCol1(value)
        assert row.count == i
    if PY2:
        rows = list(TestUnicode.select(OR(
            TestUnicode.q.col1 == u'\u00f0',
            TestUnicode.q.col2 == u'test'
        )))
        assert len(rows) == 2
        rows = list(TestUnicode.selectBy(col1=u'\u00f0', col2=u'test'))
        assert len(rows) == 0

    # starts/endswith/contains
    rows = list(TestUnicode.select(TestUnicode.q.col1.startswith("test")))
    assert len(rows) == 1
    rows = list(TestUnicode.select(TestUnicode.q.col1.endswith("test")))
    assert len(rows) == 2
    rows = list(TestUnicode.select(TestUnicode.q.col1.contains("test")))
    assert len(rows) == 2
    rows = list(TestUnicode.select(TestUnicode.q.col1.startswith(u"\u00f0")))
    assert len(rows) == 1
    rows = list(TestUnicode.select(TestUnicode.q.col1.endswith(u"\u00f0")))
    assert len(rows) == 1
    rows = list(TestUnicode.select(TestUnicode.q.col1.contains(u"\u00f0")))
    assert len(rows) == 1


def test_select():
    setup()
    _test_select()


def test_dbEncoding():
    if not PY2:
        # Python 3 mostly ignores dbEncoding
        py.test.skip("This test is for python 2")
    setup()
    TestUnicode.sqlmeta.dbEncoding = 'utf-8'
    _test_select()
    TestUnicode.sqlmeta.dbEncoding = 'latin-1'
    raises(AssertionError, _test_select)
    TestUnicode.sqlmeta.dbEncoding = 'ascii'
    raises(UnicodeEncodeError, _test_select)
    TestUnicode.sqlmeta.dbEncoding = None

    TestUnicode._connection.dbEncoding = 'utf-8'
    _test_select()
    TestUnicode._connection.dbEncoding = 'latin-1'
    raises(AssertionError, _test_select)
    TestUnicode._connection.dbEncoding = 'ascii'
    raises(UnicodeEncodeError, _test_select)
    del TestUnicode.sqlmeta.dbEncoding
    TestUnicode._connection.dbEncoding = 'utf-8'
