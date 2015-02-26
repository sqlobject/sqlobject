import sys
from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.include import hashcol
from hashlib import sha256, md5

########################################
# HashCol test
########################################

if sys.version_info[0] == 2:
    sha256_str = lambda x: sha256(x).hexdigest()
    md5_str = lambda x: md5(x).hexdigest()
else:
    sha256_str = lambda x: sha256(x.encode('utf8')).hexdigest()
    md5_str = lambda x: md5(x.encode('utf8')).hexdigest()


class HashTest(SQLObject):
    count = IntCol(alternateID=True)
    col1 = hashcol.HashCol()
    col2 = hashcol.HashCol(hashMethod=sha256_str)


data = ['test', 'This is more text', 'test 2']
items = []


def setup():
    global items
    items = []
    setupClass(HashTest)
    for i, s in enumerate(data):
        items.append(HashTest(count=i, col1=s, col2=s))


def test_create():
    setup()
    for s, item in zip(data, items):
        assert item.col1 == s
        assert item.col2 == s

    conn = HashTest._connection
    rows = conn.queryAll("""
    SELECT count, col1, col2
    FROM hash_test
    ORDER BY count
    """)
    for count, col1, col2 in rows:
        assert md5_str(data[count]) == col1
        assert sha256_str(data[count]) == col2


def test_select():
    for i, value in enumerate(data):
        rows = list(HashTest.select(HashTest.q.col1 == value))
        assert len(rows) == 1
        rows = list(HashTest.select(HashTest.q.col2 == value))
        assert len(rows) == 1
        # Passing the hash in directly should fail
        rows = list(HashTest.select(HashTest.q.col2 == sha256_str(value)))
        assert len(rows) == 0
        rows = list(HashTest.select(AND(
            HashTest.q.col1 == value,
            HashTest.q.col2 == value
        )))
        assert len(rows) == 1
        rows = list(HashTest.selectBy(col1=value))
        assert len(rows) == 1
        rows = list(HashTest.selectBy(col2=value))
        assert len(rows) == 1
        rows = list(HashTest.selectBy(col1=value, col2=value))
        assert len(rows) == 1
    rows = list(HashTest.select(OR(
        HashTest.q.col1 == 'test 2',
        HashTest.q.col2 == 'test'
    )))
    assert len(rows) == 2
