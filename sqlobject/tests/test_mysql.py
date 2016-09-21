import py.test
from sqlobject import SQLObject
from sqlobject.tests.dbtest import getConnection, setupClass


class SOTestSOListMySQL(SQLObject):
    pass


def test_list_databases():
    connection = getConnection()
    if connection.dbName != "mysql":
        py.test.skip("These tests require MySQL")
    assert connection.db in connection.listDatabases()


def test_list_tables():
    connection = getConnection()
    if connection.dbName != "mysql":
        py.test.skip("These tests require MySQL")
    setupClass(SOTestSOListMySQL)
    assert SOTestSOListMySQL.sqlmeta.table in connection.listTables()
