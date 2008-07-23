from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Schema per connection
########################################

class Test(SQLObject):
    foo = UnicodeCol(length=200)

def test_connection_schema():
    if not supports('schema'):
        return
    conn = getConnection(schema=None)
    conn.schema = None
    conn.query('CREATE SCHEMA test')
    setupClass(Test)
    Test(foo='bar')
    conn = Test._connection
    assert conn.schema, \
        """To test a schema you need to give a connection uri that contains a schema."""
    assert conn.queryAll("select * from %s.test" % conn.schema)
