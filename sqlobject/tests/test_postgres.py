import pytest
from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Test PosgreSQL sslmode
########################################


class SOTestSSLMode(SQLObject):
    test = StringCol()


def test_sslmode():
    setupClass(SOTestSSLMode)
    connection = SOTestSSLMode._connection
    if (connection.dbName != 'postgres') or \
            (not connection.module.__name__.startswith('psycopg')):
        pytest.skip("The test requires PostgreSQL, psycopg and ssl mode")

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
    connection = getConnection()
    if connection.dbName != "postgres":
        pytest.skip("These tests require PostgreSQL")
    assert connection.db in connection.listDatabases()


def test_list_tables():
    connection = getConnection()
    if connection.dbName != "postgres":
        pytest.skip("These tests require PostgreSQL")
    setupClass(SOTestSOList)
    assert SOTestSOList.sqlmeta.table in connection.listTables()
