from sqlobject import dbconnection
from firebirdconnection import FirebirdConnection

dbconnection.registerConnectionClass(
    FirebirdConnection)
