from sqlobject import dbconnection
from sybaseconnection import SybaseConnection

dbconnection.registerConnectionClass(
    SybaseConnection)
