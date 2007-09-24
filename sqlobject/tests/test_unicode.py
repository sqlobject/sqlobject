from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Unicode columns
########################################

class TestUnicode(SQLObject):
    count = IntCol(alternateID=True)
    col1 = UnicodeCol(alternateID=True)
    col2 = UnicodeCol(dbEncoding='latin-1')

data = [u'\u00f0', u'test', 'ascii test']
items = []

def setup():
    global items
    items = []
    setupClass(TestUnicode)
    for i, n in enumerate(data):
        items.append(TestUnicode(count=i, col1=n, col2=n))

def test_create():
    setup()
    for n, item in zip(data, items):
        assert item.col1 == item.col2
        assert item.col1 == n

    conn = TestUnicode._connection
    rows = conn.queryAll("""
    SELECT count, col1, col2
    FROM test_unicode
    ORDER BY count
    """)
    for count, col1, col2 in rows:
        assert data[count].encode('utf-8') == col1
        assert data[count].encode('latin1') == col2

def test_select():
    setup()
    for i, value in enumerate(data):
        rows = list(TestUnicode.select(TestUnicode.q.col1 == value))
        assert len(rows) == 1
        rows = list(TestUnicode.select(TestUnicode.q.col2 == value))
        assert len(rows) == 1
        rows = list(TestUnicode.select(AND(
            TestUnicode.q.col1 == value,
            TestUnicode.q.col2 == value
        )))
        assert len(rows) == 1
        rows = list(TestUnicode.selectBy(col1=value))
        assert len(rows) == 1
        rows = list(TestUnicode.selectBy(col2=value))
        assert len(rows) == 1
        rows = list(TestUnicode.selectBy(col1=value, col2=value))
        assert len(rows) == 1
        row = TestUnicode.byCol1(value)
        assert row.count == i
    rows = list(TestUnicode.select(OR(
        TestUnicode.q.col1 == u'\u00f0',
        TestUnicode.q.col2 == u'test'
    )))
    assert len(rows) == 2
    rows = list(TestUnicode.selectBy(col1=u'\u00f0', col2=u'test'))
    assert len(rows) == 0
