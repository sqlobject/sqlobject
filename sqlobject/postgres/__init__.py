from sqlobject import dbconnection
from pgconnection import PostgresConnection

dbconnection.registerConnectionClass(
    PostgresConnection)
