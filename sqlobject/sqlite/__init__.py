from sqlobject import dbconnection
from sqliteconnection import SQLiteConnection

dbconnection.registerConnectionClass(
    SQLiteConnection)
