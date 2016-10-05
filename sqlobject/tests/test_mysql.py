import pytest
from sqlobject import SQLObject
from sqlobject.tests.dbtest import getConnection, setupClass


class SOTestSOListMySQL(SQLObject):
    pass


def test_list_databases():
    connection = getConnection()
    if connection.dbName != "mysql":
        pytest.skip("These tests require MySQL")
    assert connection.db in connection.listDatabases()


def test_list_tables():
    connection = getConnection()
    if connection.dbName != "mysql":
        pytest.skip("These tests require MySQL")
    setupClass(SOTestSOListMySQL)
    assert SOTestSOListMySQL.sqlmeta.table in connection.listTables()
