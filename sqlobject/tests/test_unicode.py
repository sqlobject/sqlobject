from sqlobject import IntCol, SQLObject, UnicodeCol
from sqlobject.compat import PY2
from sqlobject.tests.dbtest import setupClass


########################################
# Unicode columns
########################################


class SOTestUnicode(SQLObject):
    count = IntCol(alternateID=True)
    col = UnicodeCol(alternateID=True, length=100)


data = [u'\u00f0', u'test', 'ascii test']
items = []


def setup():
    global items
    items = []
    setupClass(SOTestUnicode)
    for i, s in enumerate(data):
        items.append(SOTestUnicode(count=i, col=s))


def test_create():
    setup()
    for s, item in zip(data, items):
        assert item.col == s

    conn = SOTestUnicode._connection
    if PY2:
        rows = conn.queryAll("""
        SELECT count, col
        FROM so_test_unicode
        ORDER BY count
        """)
        for count, col in rows:
            if not isinstance(col, bytes):
                col = col.encode('utf-8')
            assert data[count].encode('utf-8') == col
    else:
        rows = conn.queryAll("""
        SELECT count, col
        FROM so_test_unicode
        ORDER BY count
        """)
        # On python 3, everthings already decoded to unicode
        for count, col in rows:
            assert data[count] == col


def test_select():
    setup()
    for i, value in enumerate(data):
        rows = list(SOTestUnicode.select(SOTestUnicode.q.col == value))
        assert len(rows) == 1
        if PY2:
            rows = list(SOTestUnicode.select(SOTestUnicode.q.col == value))
            assert len(rows) == 1
        rows = list(SOTestUnicode.selectBy(col=value))
        assert len(rows) == 1
        if PY2:
            rows = list(SOTestUnicode.selectBy(col=value))
            assert len(rows) == 1
        row = SOTestUnicode.byCol(value)
        assert row.count == i

    # starts/endswith/contains
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col.startswith("test")))
    assert len(rows) == 1
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col.endswith("test")))
    assert len(rows) == 2
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col.contains("test")))
    assert len(rows) == 2
    rows = list(SOTestUnicode.select(
        SOTestUnicode.q.col.startswith(u"\u00f0")))
    assert len(rows) == 1
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col.endswith(u"\u00f0")))
    assert len(rows) == 1
    rows = list(SOTestUnicode.select(SOTestUnicode.q.col.contains(u"\u00f0")))
    assert len(rows) == 1
