from sqlobject import *
from sqlobject.tests.dbtest import *

class TestSimple(SQLObject):

    class sqlmeta:
        registry = 'conngetter'

    name = StringCol(alternateID=True)

class TestJoined(SQLObject):

    class sqlmeta:
        registry = 'conngetter'

    this_name = StringCol(alternateID=True)
    simple = ForeignKey('TestSimple')

def test_autogetter():
    conn = getConnection(registry='conngetter')
    TestJoined.dropTable(connection=conn, ifExists=True)
    TestSimple.dropTable(connection=conn, ifExists=True)
    TestSimple.createTable(connection=conn, ifNotExists=True)
    TestJoined.createTable(connection=conn, ifNotExists=True)
    assert conn.TestSimple._soClass is TestSimple
    obj = conn.TestSimple(name='test')
    assert (TestSimple.get(obj.id, connection=conn) is obj)
    assert obj._connection is conn
    obj2 = TestSimple(name='test2', connection=conn)
    assert (conn.TestSimple.byName('test2') is obj2)
    joined = conn.TestJoined(this_name='join_test', simple=obj)
    assert joined.simple is obj
    assert joined.simple._connection is conn
    assert joined._connection is conn
    for item in conn.TestSimple.select():
        assert item._connection is conn
    
