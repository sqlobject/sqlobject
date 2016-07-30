import py.test
from sqlobject import SQLObject, UnicodeCol
from sqlobject.tests.dbtest import getConnection, setupClass, supports


########################################
# Schema per connection
########################################


class TestSchema(SQLObject):
    foo = UnicodeCol(length=200)


def test_connection_schema():
    if not supports('schema'):
        py.test.skip("schemas aren't supported")
    conn = getConnection()
    conn.schema = None
    conn.query('CREATE SCHEMA test')
    conn.schema = 'test'
    conn.query('SET search_path TO test')
    setupClass(TestSchema)
    assert TestSchema._connection is conn
    TestSchema(foo='bar')
    assert conn.queryAll("SELECT * FROM test.test_schema")
    conn.schema = None
    conn.query('SET search_path TO public')
