from sqlobject import IntCol, SQLObject
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Identity (MS SQL)
########################################


class TestIdentity(SQLObject):
    n = IntCol()


def test_identity():
    # (re)create table
    TestIdentity.dropTable(connection=getConnection(), ifExists=True)
    setupClass(TestIdentity)

    # insert without giving identity
    TestIdentity(n=100)  # i1
    # verify result
    i1get = TestIdentity.get(1)
    assert(i1get.n == 100)

    # insert while giving identity
    TestIdentity(id=2, n=200)  # i2
    # verify result
    i2get = TestIdentity.get(2)
    assert(i2get.n == 200)
