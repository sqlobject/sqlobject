from sqlobject import dbconnection
from dbmconnection import DBMConnection

dbconnection.registerConnectionClass(
    DBMConnection)
