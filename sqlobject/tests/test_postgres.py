import py.test
from sqlobject import *
from sqlobject.tests.dbtest import *


########################################
# Test PosgreSQL sslmode
########################################


class TestSSLMode(SQLObject):
    test = StringCol()


def test_sslmode():
    setupClass(TestSSLMode)
    connection = TestSSLMode._connection
    if (connection.dbName != 'postgres') or \
            (not connection.module.__name__.startswith('psycopg')):
        py.test.skip("The test requires PostgreSQL, psycopg and ssl mode")

    connection = getConnection(sslmode='require')
    TestSSLMode._connection = connection
    test = TestSSLMode(test='test')  # Connect to the DB to test sslmode

    connection.cache.clear()
    test = TestSSLMode.select()[0]
    assert test.test == 'test'


########################################
# Test PosgreSQL list{Database,Tables}
########################################


class TestSOList(SQLObject):
    pass


def test_list_databases():
    connection = getConnection()
    if connection.dbName != "postgres":
        py.test.skip("These tests require PostgreSQL")
    assert connection.db in connection.listDatabases()


def test_list_tables():
    connection = getConnection()
    if connection.dbName != "postgres":
        py.test.skip("These tests require PostgreSQL")
    setupClass(TestSOList)
    assert TestSOList.sqlmeta.table in connection.listTables()
