import pytest
from sqlobject import SQLObject, IntCol
from sqlobject.sqlbuilder import Select, ANY
from sqlobject.tests.dbtest import getConnection, setupClass


try:
    connection = getConnection()
except (AttributeError, NameError):
    # The module was imported during documentation building
    pass
else:
    if connection.dbName != "mysql":
        pytestmark = pytest.mark.skip("These tests require MySQL")


class SOTestSOListMySQL(SQLObject):
    pass


def test_list_databases():
    assert connection.db in connection.listDatabases()


def test_list_tables():
    setupClass(SOTestSOListMySQL)
    assert SOTestSOListMySQL.sqlmeta.table in connection.listTables()


class SOTestANY(SQLObject):
    value = IntCol()


def test_ANY():
    setupClass(SOTestANY)
    SOTestANY(value=10)
    SOTestANY(value=20)
    SOTestANY(value=30)
    assert len(list(SOTestANY.select(
        SOTestANY.q.value > ANY(Select([SOTestANY.q.value]))))) == 2
