import py.test
from sqlobject import SQLObject, StringCol
from sqlobject.dberrors import DuplicateEntryError, ProgrammingError
from sqlobject.tests.dbtest import getConnection, raises, setupClass, supports


########################################
# Table aliases and self-joins
########################################


class TestException(SQLObject):
    name = StringCol(unique=True, length=100)


class TestExceptionWithNonexistingTable(SQLObject):
    pass


def test_exceptions():
    if not supports("exceptions"):
        py.test.skip("exceptions aren't supported")
    setupClass(TestException)
    TestException(name="test")
    raises(DuplicateEntryError, TestException, name="test")

    connection = getConnection()
    if connection.module.__name__ != 'psycopg2':
        return
    TestExceptionWithNonexistingTable.setConnection(connection)
    try:
        list(TestExceptionWithNonexistingTable.select())
    except ProgrammingError as e:
        assert e.args[0].code == '42P01'
    else:
        assert False, "DID NOT RAISE"
