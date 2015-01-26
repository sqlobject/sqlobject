import py.test
from sqlobject import *
from sqlobject.tests.dbtest import *


class TestSOListMySQL(SQLObject):
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
    setupClass(TestSOListMySQL)
    assert TestSOListMySQL.sqlmeta.table in connection.listTables()
