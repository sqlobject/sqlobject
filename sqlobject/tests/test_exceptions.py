import pytest
from sqlobject import SQLObject, StringCol
from sqlobject.dberrors import DatabaseError, DuplicateEntryError, \
    OperationalError, ProgrammingError
from sqlobject.tests.dbtest import getConnection, raises, setupClass, supports


########################################
# Table aliases and self-joins
########################################


class SOTestException(SQLObject):
    name = StringCol(unique=True, length=100)


class SOTestExceptionWithNonexistingTable(SQLObject):
    pass


def test_exceptions():
    if not supports("exceptions"):
        pytest.skip("exceptions aren't supported")
    setupClass(SOTestException)
    SOTestException(name="test")
    raises(DuplicateEntryError, SOTestException, name="test")

    connection = getConnection()
    SOTestExceptionWithNonexistingTable.setConnection(connection)
    try:
        list(SOTestExceptionWithNonexistingTable.select())
    except ProgrammingError as e:
        assert e.args[0].code in (1146, '42P01')
    except OperationalError:
        assert connection.dbName == 'sqlite'
    except DatabaseError:
        assert connection.dbName == 'postgres' \
            and connection.driver == 'pg8000'
    else:
        assert False, "DID NOT RAISE"
