from sqlobject import dbconnection
from mysqlconnection import MySQLConnection

dbconnection.registerConnectionClass(
    MySQLConnection)
