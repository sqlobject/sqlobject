import os
import pytest
from sqlobject import SQLObject, StringCol, IntCol
from sqlobject.sqlbuilder import Select, SOME
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Test PosgreSQL sslmode
########################################


try:
    connection = getConnection()
except (AttributeError, NameError):
    # The module was imported during documentation building
    pass
else:
    if connection.dbName != "postgres":
        pytestmark = pytest.mark.skip("These tests require PostgreSQL")


class SOTestSSLMode(SQLObject):
    test = StringCol()


def test_sslmode():
    setupClass(SOTestSSLMode)
    connection = SOTestSSLMode._connection
    if (not connection.module.__name__.startswith('psycopg')) or \
            (os.name == 'nt'):
        pytest.skip("The test requires PostgreSQL, psycopg and ssl mode; "
                    "also it doesn't work on w32")

    connection = getConnection(sslmode='require')
    SOTestSSLMode._connection = connection
    test = SOTestSSLMode(test='test')  # Connect to the DB to test sslmode

    connection.cache.clear()
    test = SOTestSSLMode.select()[0]
    assert test.test == 'test'


########################################
# Test PosgreSQL list{Database,Tables}
########################################


class SOTestSOList(SQLObject):
    pass


def test_list_databases():
    assert connection.db in connection.listDatabases()


def test_list_tables():
    setupClass(SOTestSOList)
    assert SOTestSOList.sqlmeta.table in connection.listTables()


class SOTestSOME(SQLObject):
    value = IntCol()


def test_SOME():
    setupClass(SOTestSOME)
    SOTestSOME(value=10)
    SOTestSOME(value=20)
    SOTestSOME(value=30)
    assert len(list(SOTestSOME.select(
        SOTestSOME.q.value > SOME(Select([SOTestSOME.q.value]))))) == 2
