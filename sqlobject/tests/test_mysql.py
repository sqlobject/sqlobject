from sqlobject import *
from sqlobject.tests.dbtest import *

def test_list_databases():
    connection = getConnection()
    if connection.dbName != "mysql":
        return
    assert connection.db in connection.listDatabases()
