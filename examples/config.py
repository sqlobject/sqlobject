from SQLObject import *
"""
This contains basic configuration for all the examples.  Since they
all require a connection, you can configure that just in this file.
"""

## Use one of these to define your connection:
"""
conn = MySQLConnection(user='test', db='testdb')
conn = PostgresConnection('user=test dbname=testdb')
conn = SQLiteConnect('database.db')
conn = DBMConnection('database/')
"""
conn = DBMConnection('database/')
conn = MySQLConnection(user='test', db='test')
